import telebot
import time
import threading
import logging
import os
import json
import sys
from telebot.apihelper import ApiTelegramException

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoDeleteBot:
    def __init__(self, bot_name, token, channel_configs):
        self.bot_name = bot_name
        self.token = token
        self.channel_configs = channel_configs # 格式: {'-100xxx': 60, '-100yyy': 120}
        self.bot = telebot.TeleBot(token)
        
        # 注册消息处理器
        @self.bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
        def handle_post(message):
            self.process_message(message)

    def delete_message_task(self, chat_id, message_id, delay):
        """延迟删除任务"""
        time.sleep(delay)
        chat_id_str = str(chat_id)
        
        try:
            self.bot.delete_message(chat_id, message_id)
            logging.info(f"[{self.bot_name}] ✅ 已删除: 频道 {chat_id_str} | 消息 {message_id}")
        except ApiTelegramException as e:
            if e.error_code == 429: # 触发流控
                retry_after = e.result_json['parameters']['retry_after']
                logging.warning(f"[{self.bot_name}] ⚠️ 触发流控，等待 {retry_after} 秒")
                time.sleep(retry_after + 1)
                self.bot.delete_message(chat_id, message_id) # 简单的重试一次
            elif "message to delete not found" in e.description.lower():
                pass # 消息已被删，忽略
            else:
                logging.error(f"[{self.bot_name}] ❌ 删除失败: {e}")
        except Exception as e:
            logging.error(f"[{self.bot_name}] ❌ 未知错误: {e}")

    def process_message(self, message):
        """处理接收到的消息"""
        chat_id = str(message.chat.id)
        
        # 检查该频道是否在配置列表中
        if chat_id in self.channel_configs:
            delay = self.channel_configs[chat_id]
            logging.info(f"[{self.bot_name}] 📩 新消息: 频道 {chat_id} | 将在 {delay} 秒后删除")
            
            # 开启线程执行删除
            t = threading.Thread(target=self.delete_message_task, args=(message.chat.id, message.message_id, delay))
            t.daemon = True
            t.start()

    def start(self):
        """启动机器人轮询"""
        logging.info("--------------------------------")
        logging.info(f"🤖 机器人 [{self.bot_name}] 启动中...")
        logging.info(f"📋 监听频道: {list(self.channel_configs.keys())}")
        logging.info(f"⏱️ 删除延迟: {delay} 秒")
        logging.info("--------------------------------")
        try:
            self.bot.infinity_polling(timeout=10, skip_pending=True)
        except Exception as e:
            logging.error(f"[{self.bot_name}] 崩溃: {e}")

def load_config():
    """从环境变量读取并解析 JSON 配置"""
    config_str = os.getenv('BOT_CONFIG')
    if not config_str:
        logging.critical("❌ 错误: 未找到环境变量 BOT_CONFIG")
        sys.exit(1)
    
    try:
        # 尝试解析 JSON
        config_data = json.loads(config_str)
        return config_data
    except json.JSONDecodeError as e:
        logging.critical(f"❌ JSON 格式错误: {e}")
        sys.exit(1)

def run_bot_instance(cfg, index):
    """线程入口函数"""
    try:
        token = cfg.get('token')
        channels = cfg.get('channels', [])
        
        # 将频道列表转换为字典以便快速查找: {'ID': delay, ...}
        channel_map = {}
        for ch in channels:
            ch_id = str(ch.get('id'))
            delay = int(ch.get('delay', 60)) # 默认 60秒
            channel_map[ch_id] = delay
            
        bot_name = f"Bot-{index+1}"
        bot = AutoDeleteBot(bot_name, token, channel_map)
        bot.start()
    except Exception as e:
        logging.error(f"启动实例失败: {e}")

if __name__ == "__main__":
    # 读取配置
    configs = load_config()
    
    threads = []
    
    # 为每个机器人配置启动一个线程
    for i, cfg in enumerate(configs):
        t = threading.Thread(target=run_bot_instance, args=(cfg, i))
        t.daemon = True
        t.start()
        threads.append(t)
        
    # 主线程等待，防止退出
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("程序停止")
