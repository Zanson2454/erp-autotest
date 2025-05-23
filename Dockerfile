# 使用官方Python镜像
FROM m.daocloud.io/docker.io/python:3.9-slim

# 设置环境变量，优化Python和pip
# PYTHONDONTWRITEBYTECODE=1: 防止Python生成.pyc文件，减少镜像大小
# PYTHONUNBUFFERED=1: 实时输出Python日志，便于调试
# PIP_NO_CACHE_DIR=1: 不缓存pip下载的包，减少镜像大小
# PIP_DISABLE_PIP_VERSION_CHECK=1: 禁用pip版本检查，加快构建速度
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

USER root

# 使用阿里云镜像源替换Debian官方源
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources

# 安装编译工具和系统依赖
# 注：安装default-jre是因为Allure需要Java运行环境
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    wget \
    unzip \
    default-jre && \
    rm -rf /var/lib/apt/lists/*

# 配置pip镜像源
RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple/ \
    && pip config set global.trusted-host pypi.mirrors.ustc.edu.cn

# 先安装Python依赖（只复制requirements.txt，利用缓存）
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt

# 安装Allure命令行工具（使用国内镜像加速）
RUN wget https://mirrors.huaweicloud.com/repository/maven/io/qameta/allure/allure-commandline/2.24.1/allure-commandline-2.24.1.zip && \
    unzip allure-commandline-2.24.1.zip -d /opt/ && \
    ln -s /opt/allure-2.24.1/bin/allure /usr/local/bin/allure && \
    rm allure-commandline-2.24.1.zip

# 复制项目文件
COPY . /app

# 确保关键配置文件存在（如果被覆盖，重新复制）
COPY .env /app/.env
COPY pytest.ini /app/pytest.ini
COPY config/ /app/config/

# 复制启动脚本
COPY start_service.sh /app/start_service.sh
RUN chmod +x /app/start_service.sh

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["/app/start_service.sh"]