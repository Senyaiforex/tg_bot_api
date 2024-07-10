# установить Pythhon в зависимости от ОС + виртуальное окружение



# Запуск в DOCKER
    docker compose build - для сборки контейнеров
    docker compose up - для локального запуска приложения
    docker compose down -v - для удаления контейнеров 
# При необходимости перезапустить контейнер docker, его нужно остановить и
# Удалить с помощью docker compose down -v, после этого его необходимо снова пересобрать с помощью
# docker compose build и запустить docker compose up




# Running FAST API
    pip install -r requirements.txt - для установки пакетов 
    uvicorn main:app --reload для запуска приложения


# Running ngrok
    https://ngrok.com/download скачать и установить
    при запущенном FAST API - в отдельном терминале ввести команду *ngrok http 8000* для запуска ngrok
    8000 - порт, на котором запущен FAST API