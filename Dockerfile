# FROM python:3.9.4-buster
ARG PYTHON_IMAGE="registry.cn-hangzhou.aliyuncs.com/terminus/python:3.9"
FROM ${PYTHON_IMAGE}

WORKDIR /app
USER root
COPY . /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

COPY run_test.sh /app/run_test.sh
RUN chmod +x /app/run_test.sh

CMD cd /app && ls & uvicorn main:app --reload --host 0.0.0.0 --port 8000