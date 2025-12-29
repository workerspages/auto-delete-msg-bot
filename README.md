# 🗑️ Telegram Channel Auto-Delete Bot

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

一个轻量级、稳定且防封号的 Telegram 频道消息自动删除机器人。
基于 `pyTelegramBotAPI` 开发，支持 Docker 容器化一键部署，专为长期后台运行设计。

## ✨ 核心功能

*   **⏱ 精准定时删除**：支持自定义延迟时间（秒级），如发布后 2 分钟自动销毁。
*   **🛡 智能防限制 (Anti-Flood)**：自动识别 Telegram API 的频率限制（HTTP 429），触发流控时自动休眠并重试，防止被封锁。
*   **🐳 Docker 原生支持**：配置完全通过环境变量传入，支持 Docker Compose 一键启动/更新。
*   **🔒 安全启动机制**：重启时自动跳过关机期间积累的历史消息（Skip Pending），避免瞬间大量删除触发风控。
*   **📝 详细日志**：提供清晰的运行日志，方便排查权限或网络问题。

---

## 🛠️ 部署前准备

在开始之前，您需要准备：

1.  一台云服务器（VPS）或 24小时运行的电脑。
2.  已安装 **Docker** 和 **Docker Compose**（推荐）。
3.  **Bot Token**：从 [@BotFather](https://t.me/BotFather) 申请。
4.  **Channel ID**：你的频道 ID（通常以 `-100` 开头）。

> **❓ 不知道如何获取 ID？** 请查看文档底部的 [常见问题与获取 ID 指南](#-常见问题与获取-id-指南)。

---

## 🚀 快速部署 (Docker Compose) - 推荐

这是最简单、最稳妥的维护方式。

### 1. 创建项目目录
在服务器上创建一个文件夹：
```bash
mkdir tg-auto-delete
cd tg-auto-delete
```

### 2. 创建配置文件
新建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  bot:
    image: ghcr.io/workerspages/auto-delete-msg-bot:latest
    container_name: auto-delete-msg-bot
    restart: always
    # 设置时区
    environment:
      - TZ=Asia/Shanghai
      # ================= 配置区域 =================
      # 1. 你的机器人 Token
      - BOT_TOKEN=YOUR_BOT_TOKEN_HERE
      # 2. 你的频道 ID
      - CHANNEL_ID=-100xxxxxxxxxx
      # 3. 删除延迟 (秒)，例如 120 秒 = 2分钟
      - DELETE_DELAY=120
      # ===========================================
    volumes:
      - ./auto_delete_bot.py:/app/auto_delete_bot.py
      # 挂载时间，确保日志时间正确
      - /etc/localtime:/etc/localtime:ro
    working_dir: /app
    # 安装依赖并启动
    command: >
      sh -c "pip install pyTelegramBotAPI && python auto_delete_bot.py"
```

### 3. 创建代码文件
在同一目录下新建 `auto_delete_bot.py`，并将项目代码粘贴进去。（如果您已有现成的 `.py` 文件，直接上传即可）。

### 4. 启动机器人
```bash
docker-compose up -d
```

### 5. 查看运行日志
```bash
docker-compose logs -f
```
如果看到 `🤖 机器人启动成功`，恭喜你，部署完成！

---

## ⚙️ 环境变量配置说明

| 变量名 | 必填 | 默认值 | 说明 |
| :--- | :---: | :---: | :--- |
| `BOT_TOKEN` | ✅ | 无 | 机器人的 API Token (由 BotFather 提供) |
| `CHANNEL_ID` | ✅ | 无 | 目标频道的 ID (如 `-10012345678`) 或 `@用户名` |
| `DELETE_DELAY` | ❌ | `120` | 消息保留时间，单位为**秒** |
| `TZ` | ❌ | `UTC` | 系统时区，建议设为 `Asia/Shanghai` 以方便看日志 |

---

## 🐍 传统方式部署 (Python 直接运行)

如果不使用 Docker，请确保您的环境满足以下要求：

1.  **安装依赖**：
    ```bash
    pip3 install pyTelegramBotAPI
    ```
2.  **设置环境变量并运行** (Linux/Mac)：
    ```bash
    export BOT_TOKEN="你的Token"
    export CHANNEL_ID="-100xxxx"
    export DELETE_DELAY=120
    
    # 后台运行
    nohup python3 auto_delete_bot.py > bot.log 2>&1 &
    ```

---

## ❓ 常见问题与获取 ID 指南

### 1. 如何获取 Channel ID？
Telegram 的频道 ID 是固定的，即使用户名改了 ID 也不会变。
*   **方法一**：将你的频道里的任意一条消息转发给机器人 [@getmyid_bot](https://t.me/getmyid_bot)。它会返回 `Forwarded from chat: -100xxxxxxxx`，这个数字就是 ID。
*   **方法二**：在网页版 Telegram 打开频道，URL 中的数字部分（如 `c/1234567890/`）加上 `-100` 前缀即为 ID（即 `-1001234567890`）。

### 2. 机器人报错 409 Conflict？
日志提示 `Conflict: terminated by other getUpdates request`。
*   **原因**：你启动了两个机器人实例在用同一个 Token，它们在互相“打架”。
*   **解决**：
    1.  检查是否有定时任务 (Cronjob) 在重复启动脚本，**请务必删除定时任务**。
    2.  执行 `pkill -f python` 杀掉所有后台进程。
    3.  重新启动 Docker 容器。

### 3. 为什么消息没被删除？
*   请检查机器人是否已被添加为频道的 **管理员 (Admin)**。
*   请检查机器人是否有 **Delete Messages (删除消息)** 的权限。
*   查看日志，如果显示 `message to delete not found`，说明消息可能已经被其他人删除了。

---

## 👨‍💻 开发者信息

*   **Author**: Telegram Bot Enthusiast
*   **Language**: Python 3
*   **Library**: [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

如果您觉得这个脚本好用，请给个 Star ⭐！
