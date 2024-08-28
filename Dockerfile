FROM python:3.12


# Устанавливаем рабочую директорию
WORKDIR /app
# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в рабочую директорию контейнера
COPY . .

# Запускаем приложение с помощью uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]