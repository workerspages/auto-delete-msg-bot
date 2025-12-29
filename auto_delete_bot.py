import telebot
import time
import threading
import logging
import os
import sys
from telebot.apihelper import ApiTelegramException

# ================= 配置加载区域 =================
# 从环境变量读取配置，如果没有设置则报错或使用默认值
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
# 获取延迟时间，默认为 120 秒，需转换为整数
try:
    DELETE_DELAY = int(os.getenv('DELETE_DELAY', 120))
except ValueError:
    print("❌ 错误: DELETE_DELAY 必须是整数")
    sys.exit(1)

# 检查必要配置是否存在
if not BOT_TOKEN:
    print("❌ 错误: 未设置环境变量 BOT_TOKEN")
    sys.exit(1)
if not CHANNEL_ID:
    print("❌ 错误: 未设置环境变量 CHANNEL_ID")
    sys.exit(1)
# ===============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = telebot.TeleBot(BOT_TOKEN)

def delete_message_task(chat_id, message_id):
    """延迟删除任务"""
    time.sleep(DELETE_DELAY)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            bot.delete_message(chat_id, message_id)
            logging.info(f"✅ 成功删除: ID {message_id}")
            break
        except ApiTelegramException as e:
            if e.error_code == 429: # 限流
                retry_after = e.result_json['parameters']['retry_after']
                logging.warning(f"⚠️ 触发流控，等待 {retry_after} 秒")
                time.sleep(retry_after + 1)
                continue
            elif "message to delete not found" in e.description.lower():
                break # 已经被删了
            elif "message can't be deleted" in e.description.lower():
                logging.error(f"❌ 权限不足，无法删除")
                break
            else:
                logging.error(f"❌ 删除失败: {e}")
                break
        except Exception as e:
            logging.error(f"❌ 系统错误: {e}")
            break

@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
def handle_channel_post(message):
    try:
        # 验证是否是目标频道
        is_target = False
        if str(message.chat.id) == str(CHANNEL_ID):
            is_target = True
        elif message.chat.username and ('@' + message.chat.username) == CHANNEL_ID:
            is_target = True
        elif CHANNEL_ID == 'ALL': # 特殊开关：允许监听机器人所在的任何频道
            is_target = True

        if is_target:
            logging.info(f"📩 收到新消息: ID {message.message_id}，将在 {DELETE_DELAY} 秒后删除")
            t = threading.Thread(target=delete_message_task, args=(message.chat.id, message.message_id))
            t.daemon = True
            t.start()
    except Exception as e:
        logging.error(f"处理错误: {e}")

if __name__ == "__main__":
    logging.info("--------------------------------")
    logging.info(f"🤖 机器人启动成功")
    logging.info(f"🎯 监听频道: {CHANNEL_ID}")
    logging.info(f"⏱️ 删除延迟: {DELETE_DELAY} 秒")
    logging.info("--------------------------------")
    
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        logging.critical(f"机器人崩溃: {e}")
