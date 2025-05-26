# 使用 DaoCloud 国内代理的官方 Python 3.9 slim 镜像，拉取速度快
FROM m.daocloud.io/docker.io/python:3.9-slim

# 设置环境变量，优化 Python 和 pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 使用阿里云加速 apt-get，安装 Java 运行环境和必要工具
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends openjdk-11-jre-headless wget unzip && \
    rm -rf /var/lib/apt/lists/*

# 配置 pip 源为中科大，加速 Python 包下载
RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip config set global.trusted-host pypi.mirrors.ustc.edu.cn

# 先安装 Python 依赖，充分利用 Docker 缓存
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 安装 Allure CLI（用国内华为云镜像）
ENV ALLURE_VERSION=2.24.1
RUN wget --timeout=1200 --tries=3 https://mirrors.huaweicloud.com/repository/maven/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip && \
    unzip allure-commandline-${ALLURE_VERSION}.zip -d /opt/ && \
    ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure && \
    rm allure-commandline-${ALLURE_VERSION}.zip

# 只复制生产需要的代码（建议用 .dockerignore 排除无关文件）
COPY . /app

# 设置 JAVA_HOME 环境变量，方便 Java 工具自动识别
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# 暴露服务端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

