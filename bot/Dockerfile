# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /bot

# Копируем файлы, относящиеся к боту
COPY ./bot/requirements.txt /bot/requirements.txt
COPY ./bot /bot


RUN pip install --upgrade pip
RUN pip install -r /bot/requirements.txt

# Создаем символические ссылки на общие модули
RUN ln -s /models /bot/models \
    && ln -s /repository /bot/repository \
    && ln -s /utils /bot/utils \
    && ln -s /database.py /bot/database.py

# Указываем команду запуска бота
CMD ["python", "bot_main.py"]