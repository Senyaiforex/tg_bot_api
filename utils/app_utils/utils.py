import requests

async def check_task_complete(telegram_id: int, task_id: int) -> bool:
    url = f'http://bot:8443/check_task/{telegram_id}/{task_id}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()  # Преобразуем ответ в формат JSON
        complete = data.get('complete')  # Извлекаем значение из поля 'complete'
        return complete
    else:
        return False
