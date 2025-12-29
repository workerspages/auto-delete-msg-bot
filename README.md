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
cd auto-delete-msg-bot
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
      # 配置你的机器人 Token 和 频道 id
      - BOT_CONFIG=[{"token":"123456:AAA-机器人A","channels":[{"id":"-100111","delay":60},{"id":"-100222","delay":300}]},{"token":"987654:BBB-机器人B","channels":[{"id":"-100333","delay":10}]}]
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
| `BOT_CONFIG` | ✅ | 无 | [{"token":"123456:AAA-机器人A","channels":[{"id":"-100111","delay":60},{"id":"-100222","delay":300}]},{"token":"987654:BBB-机器人B","channels":[{"id":"-100333","delay":10}]}] |
| `TZ` | ❌ | `UTC` | 系统时区，建议设为 `Asia/Shanghai` 以方便看日志 |



### 配置方式 (JSON)

因为要支持复杂结构，使用这种单一变量，而是合并为一个名为 `BOT_CONFIG` 的变量，其内容是一个 **JSON 列表**。

#### 示例配置格式

假设你有两个机器人：
*   **机器人 A**：
    *   管理频道 `-1001111`，2分钟（120秒）删除。
    *   管理频道 `-1002222`，5分钟（300秒）删除。
*   **机器人 B**：
    *   管理频道 `-1003333`，10秒删除（快闪模式）。

你需要构造如下的 JSON 字符串：

```json
[
  {
    "token": "机器人A的TOKEN",
    "channels": [
      {"id": "-1001111", "delay": 120},
      {"id": "-1002222", "delay": 300}
    ]
  },
  {
    "token": "机器人B的TOKEN",
    "channels": [
      {"id": "-1003333", "delay": 10}
    ]
  }
]
```

---

### 3. 如何在 Zeabur (或其他平台) 上部署

#### 第一步：重新构建镜像
由于代码变了，你需要重新 Commit 代码并 Push 到 GitHub，或者重新运行我之前提供的 Shell 脚本来生成镜像。
`Dockerfile` **不需要修改**，依然是那个样子。

#### 第二步：修改环境变量

在 Zeabur 的 **Variables** 面板中：

1.  **新增** 变量 `BOT_CONFIG`。
2.  **填入值**：将上面的 JSON 代码压缩成一行（或者 Zeabur 支持多行输入），填进去。

**Zeabur 填写的示例值（压缩版）：**
```text
[{"token":"123456:AAA-机器人A","channels":[{"id":"-100111","delay":60},{"id":"-100222","delay":300}]},{"token":"987654:BBB-机器人B","channels":[{"id":"-100333","delay":10}]}]
```
```text
[{"token":"A机器人Token","channels":[{"id":"A群组或频道ID","delay":延迟删除时间秒},{"id":"B群组或频道ID","delay":延迟删除时间秒}]},{"token":"B机器人Token","channels":[{"id":"C群组或频道ID","delay":延迟删除时间秒}]}]
```


### 4. 常见问题 (FAQ)

**Q: 为什么我填了之后报错 JSON 格式错误？**
A: JSON 对格式要求很严。
1.  必须用**双引号** `"`，不能用单引号 `'`。
2.  最后一个元素后面**不能有逗号**。
3.  建议在电脑上的记事本里先写好，去 [JSON校验网站](https://www.json.cn/) 验证一下格式，再复制到 Zeabur。

**Q: 我可以用一个机器人管理 10 个频道吗？**
A: 可以。只要在 `channels` 列表里继续添加 `{ "id": "...", "delay": ... }` 即可。

**Q: 多个机器人会冲突吗？**
A: 不会。这个脚本使用了多线程（Threading），每个机器人在独立的线程里运行，互不干扰。


---

## 👨‍💻 开发者信息

*   **Author**: Telegram Bot Enthusiast
*   **Language**: Python 3
*   **Library**: [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

如果您觉得这个脚本好用，请给个 Star ⭐！
