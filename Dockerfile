# 使用官方轻量级 Python 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# PYTHONDONTWRITEBYTECODE: 不生成 .pyc 文件
# PYTHONUNBUFFERED: 1 确保日志直接输出到控制台，不会被缓存（方便看日志）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 安装时区数据（可选，为了日志时间正确）
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 先只复制依赖文件，利用 Docker 缓存层加速构建
COPY requirements.txt .

# 安装依赖
# --no-cache-dir 减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下所有文件到容器
COPY . .

# 启动命令
CMD ["python", "auto_delete_bot.py"]
