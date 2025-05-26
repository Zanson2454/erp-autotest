# FROM python:3.9.4-buster
ARG PYTHON_IMAGE="registry.cn-hangzhou.aliyuncs.com/terminus/python:3.9"
FROM ${PYTHON_IMAGE}

WORKDIR /app
USER root
COPY . /app

# 配置 pip 使用阿里云镜像
RUN mkdir -p /root/.pip && \
    echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/" > /root/.pip/pip.conf

# 只用 requirements.txt 安装所有依赖
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --timeout 120

# 安装 Java（Allure CLI 依赖 Java）
RUN apt-get update && apt-get install -y openjdk-11-jre wget unzip \
    && wget https://github.com/allure-framework/allure2/releases/download/2.27.0/allure-2.27.0.tgz \
    && tar -zxvf allure-2.27.0.tgz -C /opt/ \
    && ln -s /opt/allure-2.27.0/bin/allure /usr/bin/allure

# 只启动 uvicorn 服务，测试请在 CI/CD 流水线单独执行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

