# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы, относящиеся к FastAPI
COPY ./app/requirements.txt /app/requirements.txt
COPY ./app /app

# Устанавливаем зависимости
RUN pip install -r /app/requirements.txt

# Создаем символические ссылки на общие модули
RUN ln -s /models /app/models \
    && ln -s /repository /app/repository \
    && ln -s /utils /app/utils \
    && ln -s /database.py /app/database.py
# Указываем команду запуска FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]