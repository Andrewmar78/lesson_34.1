# Базовый образ
FROM python:3.10-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
COPY . .
CMD  python3 todolist/manage.py runserver -h 0.0.0.0 -p 80
