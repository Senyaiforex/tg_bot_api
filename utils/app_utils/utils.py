import math
from datetime import datetime, date
from typing import Any

import aiohttp
from dataclasses import dataclass

from pydantic import BaseModel

from repository import TaskRepository, UserRepository, PostRepository, SellerRepository
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


# async def categorize_tasks(tasks: list) -> dict:
#     categorized_tasks = defaultdict(lambda: {'countTasks': 0, 'tasks': []})
#     for task in tasks:
#         task_type = str(task.type_task.code)
#         categorized_tasks[task_type]["tasks"].append({
#                 'id': task.id,
#                 'description': task.description,
#                 'url': task.url,
#                 'type_task': task.type_task.code
#
#         })
#         categorized_tasks[task_type]['countTasks'] += 1
#     return dict(categorized_tasks)


@dataclass(frozen=True)
class LiquidData:
    free_liq = 33
    coins_liq = 33
    money_liq = 33
    token_liq = 33


liquid_const = LiquidData()


async def create_data_posts(session: async_session,
                            today_count: int | None = None) -> list[dict[str: Any],]:
    """
    Функция для создания информации по количествам опубликованных постов
    за месяц
    Ответ:
    - name - Вид публикации
    - price - Стоимость публикации
    - data - Данные о ликвидности [сколько сейчас опубликовано, сколько осталось до выполнения плана] в
    процентном соотношении %
    - current - Текущее количество публикаций
    - need - Требуемое количество публикаций
    :return:
    """
    liquid_instance = await PostRepository.get_liquid_posts(session)
    dict_type_posts = {
            0: ('Посты бесплатно', liquid_instance.free_posts,
                liquid_instance.current_free, 0),
            1: ('Посты за токены', liquid_instance.token_posts,
                liquid_instance.current_token, 750),
            2: ('Посты за монеты', liquid_instance.coins_posts,
                liquid_instance.current_coins, 10000),
            3: ('Посты за рубли', liquid_instance.money_posts,
                liquid_instance.current_money, 1000),
            4: ('Посты за звёзды', liquid_instance.stars_posts,
                liquid_instance.current_stars, 30)
    }
    list_models = []
    for index in range(5):
        current_percent = min(int(dict_type_posts[index][2] / dict_type_posts[index][1] * 100), 100)
        need_percent = max(100 - current_percent, 0)
        list_models.append({
                "name": dict_type_posts[index][0],
                "price": dict_type_posts[index][2] * dict_type_posts[index][3],
                "data": [current_percent, need_percent],
                "current": dict_type_posts[index][2],
                "need": dict_type_posts[index][1]
        })
    if today_count or today_count == 0:
        post_by_sellers = await SellerRepository.get_count_sellers(session)
        current_percent = min(int((today_count + post_by_sellers) / 200 * 100), 100)
        need_percent = max(100 - current_percent, 0)
        list_models.append({
                "name": 'Посты за день',
                "price": 0,
                "data": [current_percent, need_percent],
                "current": today_count + post_by_sellers,
                "need": 200
        })
    return list_models


async def create_data_pull(pull: Pull) -> dict[str: tuple[int]]:
    """
    Функция создаёт данные для отображения текушего пула
    и отношения текушего пула к максимальному
    :param pull: инстанс Пула
    :return: dict
    """
    dict_data_pull = {
            "farming": (pull.farming, pull.current_farming, int(pull.current_farming / pull.farming * 100)),
            "tasks": (pull.tasks, pull.current_tasks, int(pull.current_tasks / pull.tasks * 100)),
            "friends": (pull.friends, pull.current_friends, int(pull.current_friends / pull.friends * 100)),
            "coins": (pull.coins, pull.current_coins, int(pull.current_coins / pull.coins * 100)),
            "plan": (pull.plan, pull.current_plan, int(pull.current_plan / pull.plan * 100))
    }
    return dict_data_pull


dict_cat = {'task': 'Задания',
            'subscribe': "Подписки",
            "watch": "Видео",
            "games": "Игры",
            "bonus": "Бонусы"}


async def create_data_tasks(task_validator: BaseModel,
                            category_validator: BaseModel,
                            telegram_id: int,
                            session: async_session) -> list[BaseModel]:
    """
    Функция создаёт данные для отображения типов задач
    :param task_validator: Схема pydantic для валидации задач
    :param category_validator: Схема pydantic для валидации категорий
    :param telegram_id: Айди телеграм пользователя
    :param session: Асинхронная сессия
    :return: Список схем pydantic - категории
    :rtype: list[BaseModel]
    """
    categories = await TaskRepository.get_categories_with_tasks(session)
    user = await UserRepository.get_user_with_tasks(telegram_id, session)
    user_tasks_ids = {task.id for task in user.tasks} if user else set()
    date_today = datetime.today().date()
    categories_output = []
    completed_tasks = []
    for category in categories:
        # Фильтр задач
        tasks_not_completed = []
        for task in category.tasks:
            if task.id not in user_tasks_ids and date_today <= task.date_limit and task.active:
                tasks_not_completed.append(task_validator(id=task.id,
                                                          description=task.description,
                                                          url=task.url,
                                                          reward=task.reward))
            elif task.id in user_tasks_ids:
                completed_tasks.append(task_validator(id=task.id,
                                                      description=task.description,
                                                      url=task.url,
                                                      reward=task.reward))

        categories_output.append(category_validator(
                id=category.id,
                name=dict_cat[category.name],
                tasks=tasks_not_completed
        ))
    categories_output.append(category_validator(
            id=6,
            name='Завершённые',
            tasks=completed_tasks
    ))
    return categories_output


async def calculate_percent(value_one: int, value_two: int) -> str:
    """
    Функция считает процентную разницу между двумя числами относительно второго числа.
    Второе число берется как 100%. Округление всегда происходит в большую сторону.
    :param value_one: первое число
    :param value_two: второе число
    :return: процентная разница со знаком + или -, либо 0 если числа равны
    :rtype: str
    """
    try:
        if value_one == value_two:
            return "0"

        percent_difference = ((value_one - value_two) / value_two) * 100
        rounded_difference = math.ceil(abs(percent_difference))
        if rounded_difference == 0:
            rounded_difference = 1
        sign = "+" if percent_difference > 0 else "-"

        return f"{sign}{rounded_difference}%"

    except ZeroDivisionError:
        return "0"


async def create_data_liquid(session: async_session) -> dict[str: int | str]:
    """
    Функция создаёт данные для формирования данных о пуле ликвидности постов
    за месяц
    :param session: Асинхронная сессия
    :return: словарь с параметрами
    :rtype: dict
    """
    liquid_instance = await PostRepository.get_liquid_posts(session)
    all_public_need = (liquid_instance.money_posts +  # сколько всего постов необходимо опубликовать
                       liquid_instance.token_posts +
                       liquid_instance.coins_posts +
                       liquid_instance.free_posts +
                       liquid_instance.stars_posts)
    paid_public_need = (liquid_instance.money_posts +  # сколько платных постов необходимо опубликовать
                        liquid_instance.token_posts +
                        liquid_instance.coins_posts +
                        liquid_instance.stars_posts)
    free_public_need = liquid_instance.free_posts  # сколько бесплатных постов необходимо опубликовать
    all_current = sum(
            getattr(liquid_instance, attr) for attr
            in dir(liquid_instance) if attr.startswith("current")
    )
    paid_current = sum(
            getattr(liquid_instance, attr) for attr
            in dir(liquid_instance) if attr.startswith("current") and 'free' not in attr
    )
    data_liquid_posts = {
            'all_posts': {
                    'need': all_public_need,
                    'current': all_current,
                    'percent': await calculate_percent(all_current, all_public_need)},
            'paid_posts': {
                    'need': paid_public_need,
                    'current': paid_current,
                    'percent': await calculate_percent(paid_current, paid_public_need)},
            'free_posts': {
                    'need': free_public_need,
                    'current': liquid_instance.current_free,
                    'percent': await calculate_percent(liquid_instance.current_free, free_public_need)}
    }
    return data_liquid_posts


async def get_friend_word(number: int) -> str:
    endings = {
            1: "друга", 2: "друга",
            3: "друга", 4: "друга",
            0: "друзей", 5: "друзей",
            6: "друзей", 7: "друзей",
            8: "друзей", 9: "друзей"
    }
    if 11 <= number % 100 <= 14:
        return "друзей"
    # Окончание по последней цифре
    return endings[number % 10]
