# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы, относящиеся к FastAPI
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
COPY . /app
RUN chmod +x /app/apply_migrations.sh

ENTRYPOINT ["sh", "/app/apply_migrations.sh"]