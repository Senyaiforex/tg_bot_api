import requests
from collections import defaultdict
import asyncio
import aiohttp

async def check_task_complete(telegram_id: int, task_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        url = f'http://bot:8443/check_task/{telegram_id}/{task_id}'
        response = await session.get(url)
    if response.status == 200:
        data = response.json()
        complete = data.get('complete')
        return complete
    else:
        return False


async def categorize_tasks(tasks: list) -> dict:
    categorized_tasks = defaultdict(lambda: {'countTasks': 0, 'tasks': []})
    for task in tasks:
        task_type = str(task.type_task.code)
        categorized_tasks[task_type]["tasks"].append({
                'id': task.id,
                'description': task.description,
                'url': task.url,
                'type_task': task.type_task.code

        })
        categorized_tasks[task_type]['countTasks'] += 1
    return dict(categorized_tasks)
