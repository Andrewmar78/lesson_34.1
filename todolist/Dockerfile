# Базовый образ
FROM python:3.10-slim

# Рабочий каталог
WORKDIR /code

# Снижаем размер Docker-файла:
# Исключаем создание кэша, прописываем путь для запуска процедур в контейнере
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PYTHON_PATH=/code

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Создаем группу service, добавляем пользователя api для исключения работ из root
RUN groupadd --system service && useradd --system -g service api

# Копируем все
COPY  ./ ./
COPY entrypoint.sh ./entrypoint.sh

# Задаем пользователя
USER api

# Создаем код, который выполнится до запуска контейнера. Чтобы не создавать контейнер с миграциями
ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Указываем внешний порт
EXPOSE 8000

#COPY requirements.txt .
#RUN pip install --upgrade pip
#RUN python3 -m pip install -r requirements.txt
#COPY . .
#CMD  python3 todolist/manage.py runserver -h 0.0.0.0 -p 80
