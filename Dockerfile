# FROM python:3.9.4-buster
#ARG PYTHON_IMAGE="registry.cn-hangzhou.aliyuncs.com/terminus/python:3.9"
FROM m.daocloud.io/docker.io/python:3.9-slim

WORKDIR /app
USER root
COPY . /app

COPY requirements.txt /app/requirements.txt
# 更新 pip 并安装依赖，确保使用 python -m pip 安装
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    python -m pip install uvicorn fastapi -i https://pypi.mirrors.ustc.edu.cn/simple/

COPY run_test.sh /app/run_test.sh
RUN chmod +x /app/run_test.sh

# 使用 python -m 来启动 uvicorn
CMD cd /app && ls && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000