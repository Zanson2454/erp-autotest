# FROM python:3.9.4-buster
ARG PYTHON_IMAGE="registry.cn-hangzhou.aliyuncs.com/terminus/python:3.9"
FROM ${PYTHON_IMAGE}

WORKDIR /app
USER root
COPY . /app

# 优先用 requirements.txt 安装依赖（如果有）
COPY requirements.txt /app/requirements.txt
RUN if [ -f requirements.txt ]; then \
    pip install --upgrade pip && \
    pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/; \
fi

# 补充常用依赖（如 requirements.txt 不全）
RUN pip install fastapi -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install uvicorn -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install faker -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install xmltodict==0.13.0 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install requests==2.28.2 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install python-multipart==0.0.5 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install pydantic==1.10.4 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install loguru -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install pyecharts==2.0.2 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install pandas -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install openpyxl==3.1.2 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install DingtalkChatbot==1.5.7 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install pytz==2022.7.1 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install pyppeteer==1.0.2 -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install PyYAML==6.0  -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install swagger_parser -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install selenium -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install webdriver-manager -i https://pypi.mirrors.ustc.edu.cn/simple/ && \
    pip install Pillow -i https://pypi.mirrors.ustc.edu.cn/simple/

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

