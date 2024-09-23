from collections import defaultdict
import aiohttp
from dataclasses import dataclass

from pydantic import BaseModel
from repository import TaskRepository, UserRepository
from database import async_session
from models import Pull


async def check_task_complete(telegram_id: int, task_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        url = f'http://bot:8443/check_task/{telegram_id}/{task_id}'
        response = await session.get(url)
        if response.status == 200:
            data = await response.json()
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
    free_liq = 33
    coins_liq = 33
    money_liq = 33
    token_liq = 33


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

        list_models.append({
                "name": dict_type_posts[index][0],
                "price": dict_type_posts[index][2],
                "data": [current_percent, need_percent],
                "current": posts_count[index],
                "need": dict_type_posts[index][1]
        })
    return list_models


async def create_data_pull(pull: Pull):
    dict_data_pull = {
            "farming": (pull.farming, pull.current_farming, int(pull.current_farming / pull.farming * 100)),
            "tasks": (pull.task, pull.current_task, int(pull.current_task / pull.task * 100)),
            "friends": (pull.friends, pull.current_friends, int(pull.current_friends / pull.friends * 100)),
            "coins": (pull.coins, pull.current_coins, int(pull.current_coins / pull.coins * 100)),
            "plan": (pull.plan, pull.current_plan, int(pull.current_plan / pull.plan * 100))
    }
    return dict_data_pull


async def create_data_tasks(task_validator: BaseModel,
                            category_validator: BaseModel,
                            telegram_id: int,
                            session: async_session) -> list[BaseModel]:
    categories = await TaskRepository.get_categories_with_tasks(session)
    user = await UserRepository.get_user_with_tasks(telegram_id, session)
    user_tasks_ids = {task.id for task in user.tasks} if user else set()
    categories_output = []
    completed_tasks = []
    for category in categories:
        # Фильтр задач
        tasks_not_completed = []
        for task in category.tasks:
            if task.id not in user_tasks_ids:
                tasks_not_completed.append(task_validator(id=task.id, description=task.description, url=task.url))
            else:
                completed_tasks.append(task_validator(id=task.id, description=task.description, url=task.url))

        categories_output.append(category_validator(
                id=category.id,
                name=category.name,
                tasks=tasks_not_completed
        ))
    categories_output.append(category_validator(
            id=8,
            name='completed',
            tasks=completed_tasks
    ))
    return categories_output
