# 使用阿里云 Python 镜像（如无特殊需求可用官方 python:3.9-slim）
ARG PYTHON_IMAGE="ghcr.io/tiangolo/python3.9-jdk:latest"
FROM ${PYTHON_IMAGE}

WORKDIR /app

# 只拷贝必要文件，减少构建上下文
COPY requirements.txt ./
RUN mkdir -p /root/.pip && \
    echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/" > /root/.pip/pip.conf && \
    pip install -r requirements.txt --timeout 120

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

