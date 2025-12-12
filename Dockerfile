# DownList Docker 镜像
# 基于 Python 3.11 slim 镜像

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLET_SERVER_PORT=8550
ENV FLET_FORCE_WEB_VIEW=true

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p /app/downloads /app/data

# 暴露端口
EXPOSE 8550

# 设置数据卷
VOLUME ["/app/downloads", "/app/data"]

# 启动命令 - 使用 Web 模式
CMD ["python", "-m", "flet", "run", "--web", "--port", "8550", "main.py"]
