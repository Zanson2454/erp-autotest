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

# 只启动 uvicorn 服务，测试请在 CI/CD 流水线单独执行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

