# FROM python:3.9.4-buster
ARG PYTHON_IMAGE="registry.cn-hangzhou.aliyuncs.com/terminus/python:3.9"
FROM ${PYTHON_IMAGE}

WORKDIR /app
USER root
COPY . /app

# 只用 requirements.txt 安装所有依赖
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

# 先运行所有测试用例并生成 Allure 报告，全部通过后再启动服务
CMD pytest --alluredir=reports/allure-results testcases && \
    allure generate reports/allure-results -o reports/allure-report --clean && \
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

