# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы, относящиеся к FastAPI
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
COPY . /app
RUN chmod +x /app/apply_migrations.sh

# Создаем символические ссылки на общие модули
RUN ln -s /models /app/models \
    && ln -s /repository /app/repository \
    && ln -s /utils /app/utils \
    && ln -s /database.py /app/database.py \

ENTRYPOINT ["sh", "app/apply_migrations.sh"]