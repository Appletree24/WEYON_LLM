FROM python:3.11-slim-bullseye
LABEL authors="weyon"

EXPOSE 7860

WORKDIR /app

COPY requirements.txt /app/requirements.txt

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ /app

WORKDIR /app/src


ENTRYPOINT ["python", "main.py"]