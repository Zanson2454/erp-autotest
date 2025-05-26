# 使用阿里云 Python 镜像（如无特殊需求可用官方 python:3.9-slim）
ARG PYTHON_IMAGE="registry.erda.cloud/trantor/python-jre:3.9"
FROM ${PYTHON_IMAGE}

WORKDIR /app


# 安装Allure命令行工具（使用国内镜像加速）
RUN wget https://mirrors.huaweicloud.com/repository/maven/io/qameta/allure/allure-commandline/2.24.1/allure-commandline-2.24.1.zip && \
    unzip allure-commandline-2.24.1.zip -d /opt/ && \
    ln -s /opt/allure-2.24.1/bin/allure /usr/local/bin/allure && \
    rm allure-commandline-2.24.1.zip

# 只拷贝必要文件，减少构建上下文
COPY requirements.txt ./
RUN mkdir -p /root/.pip && \
    echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/" > /root/.pip/pip.conf && \
    pip install -r requirements.txt --timeout 120

# 再拷贝项目代码（避免每次代码变动都重新装依赖）
COPY . .

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

