# 使用阿里云 Python 镜像（如无特殊需求可用官方 python:3.9-slim）
ARG PYTHON_IMAGE="registry.erda.cloud/trantor/python-jre:3.9"
FROM ${PYTHON_IMAGE}

WORKDIR /app


ARG ALLURE_VERSION=2.24.0
RUN wget -q https://mirrors.tuna.tsinghua.edu.cn/allure/binaries/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip \
    && unzip allure-commandline-${ALLURE_VERSION}.zip -d /opt \
    && mv /opt/allure-commandline-${ALLURE_VERSION} /opt/allure \
    && ln -s /opt/allure/bin/allure /usr/bin/allure \
    && rm allure-commandline-${ALLURE_VERSION}.zip

# 只拷贝必要文件，减少构建上下文
COPY requirements.txt ./
RUN mkdir -p /root/.pip && \
    echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/" > /root/.pip/pip.conf && \
    pip install -r requirements.txt --timeout 120

# 再拷贝项目代码（避免每次代码变动都重新装依赖）
COPY . .

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

