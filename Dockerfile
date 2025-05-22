# 使用官方Python镜像
FROM m.daocloud.io/docker.io/python:3.9-slim

WORKDIR /app
USER root
COPY . /app

COPY requirements.txt /app/requirements.txt
# 更新 pip 并安装依赖，确保使用 python -m pip 安装
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

COPY run_test.sh /app/run_test.sh
RUN chmod +x /app/run_test.sh

# 直接运行测试脚本
CMD ["/app/run_test.sh"]