# 使用阿里云 Python 镜像（如无特殊需求可用官方 python:3.9-slim）
ARG PYTHON_IMAGE="registry.cn-hangzhou.aliyuncs.com/terminus/python:3.9"
FROM ${PYTHON_IMAGE}

WORKDIR /app

# 只拷贝必要文件，减少构建上下文
COPY requirements.txt ./
RUN mkdir -p /root/.pip && \
    echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/" > /root/.pip/pip.conf && \
    pip install -r requirements.txt --timeout 120

# 再拷贝项目代码（避免每次代码变动都重新装依赖）
COPY . .

# 安装系统依赖和 Allure CLI（合并为一个 RUN，减少镜像层数）
ENV ALLURE_VERSION=2.24.1
RUN sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org|http://mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        wget unzip default-jre \
    && wget https://mirrors.huaweicloud.com/repository/maven/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip \
    && unzip allure-commandline-${ALLURE_VERSION}.zip -d /opt/ \
    && ln -sf /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure \
    && rm allure-commandline-${ALLURE_VERSION}.zip \
    && apt-get purge -y wget unzip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Python 运行环境变量优化
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

