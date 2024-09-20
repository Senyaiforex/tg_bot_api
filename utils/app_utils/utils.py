import requests
from collections import defaultdict
import asyncio
import aiohttp
from dataclasses import dataclass
from pydantic import BaseModel, Field


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


@dataclass(frozen=True)
class LiquidData:
    free_liq = 80
    coins_liq = 60
    money_liq = 50
    token_liq = 30


liquid_const = LiquidData()

async def create_data_posts(posts_count: list[int]) -> list[dict]:
    dict_type_posts = {
            0: ('Посты бесплатно', liquid_const.free_liq, 0),
            1: ('Посты за токены', liquid_const.token_liq, 750),
            2: ('Посты за монеты', liquid_const.coins_liq, 10000),
            3: ('Посты за рубли', liquid_const.money_liq, 1000)
    }
    list_models = []
    for index in range(len(posts_count)):
        current_percent = int(posts_count[index] / dict_type_posts[index][1] * 100)
        need_percent = 100 - current_percent
        print(current_percent, need_percent)
        list_models.append({
                'name': dict_type_posts[index][0],
                'price': dict_type_posts[index][2],
                'data': [current_percent, need_percent]
        })
    return list_models
