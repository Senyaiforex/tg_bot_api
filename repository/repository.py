from typing import List, Dict, Union

from fastapi import HTTPException
from database import async_session
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models import User, HistoryTransaction, Task


async def get_user_by_telegram_id(telegram_id: int, session: async_session) -> User:
    """
    Функция дял получения пользователя из базы данных по id_telegram
    :param telegram_id:
    :param session:
    :return:
    """
    result = await session.execute(
            select(User)
            .options(joinedload(User.friends))  # Подгружаем друзей вместе с пользователем
            .where(User.id_telegram == telegram_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def base_create_user(user: User, session: async_session) -> User:
    """
    Функция для создания нового пользователя в базе данных
    :param user:
    :param session:
    :return:
    """
    new_user = User(
            id_telegram=user.id_telegram,
            user_name=user.user_name,
            count_coins=user.count_coins,
            count_pharmd=user.count_pharmd,
            count_invited_friends=user.count_invited_friends,
            purchase_count=user.purchase_count,
            sale_count=user.sale_count,
    )
    result = await session.execute(select(User). \
                                   where(User.id_telegram == new_user.id_telegram))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def get_task_by_id(task_id: int, session: async_session) -> Task:
    result = await session.execute(
            select(Task)
            .where(Task.id == task_id)
    )
    task = result.scalars().first()
    return task


async def add_task(user: User, task: Task, session):
    if task not in user.tasks:
        user.tasks.append(task)
        await session.commit()


async def create_task(url: str, description: str, type_task: str, session: async_session) -> bool:
    """
    ��ункция для создания новой задачи в базе данных
    :param url:
    :param description:
    :param type_task:
    :return:
    """
    new_task = Task(
            url=url,
            description=description,
            type_task=type_task,
    )
    session.add(new_task)
    await session.commit()
    return True


async def get_tasks_by_type(type_task: str, session) -> list[Task]:
    result = await session.execute(
            select(Task)
            .where(Task.type_task == type_task)
    )
    tasks = result.scalars().all()
    return tasks


async def change_coins_by_id(
        id_telegram: int,
        amount: int,
        add: bool,
        session: async_session
) -> User:
    """
    Функция для изменения количества токенов у пользователя
    по его id_telegram
    :param telegram_id:
    :param amount:
    :param add:
    :param session:
    :return:
    """
    user = await get_user_by_telegram_id(id_telegram, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if add:
        description = "#Описание транзакции(позже)"
        await user.update_count_coins(session, amount, description)
    else:
        user.count_coins -= amount
        await session.commit()
    return user


async def change_pharmd_by_id(
        id_telegram: int,
        amount: int,
        add: bool,
        session: async_session
) -> User:
    """
    Функция для изменения количества токенов у пользователя
    по его id_telegram
    :param telegram_id:
    :param amount:
    :param add:
    :param session:
    :return:
    """
    user = await get_user_by_telegram_id(id_telegram, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if add:
        user.count_pharmd += amount
    else:
        user.count_pharmd -= amount
    await session.commit()
    return user


async def create_user_tg(id_telegram: int, username: str, session: async_session) -> None:
    """
    Функция для создания нового пользователя в базе данных из телеграмма.
    :param id_telegram: id_telegram пользователя
    :param username: username пользователя
    :param session:
    :return:
    """
    new_user = User(
            id_telegram=id_telegram,
            user_name=username,
    )
    result = await session.execute(select(User). \
                                   where(User.id_telegram == new_user.id_telegram))
    user = result.scalars().first()
    if user:
        return
    else:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)


async def get_friends(id_telegram: int, session) -> List[Dict[str, Union[int, str]]]:
    """
    Получить список друзей пользователя с заданным id_telegram.
    :param id_telegram: ID пользователя в Telegram.
    :param session: Сессия базы данных.
    :return: Список друзей с их username, count_coins и level.
    """
    # Находим пользователя по id_telegram
    result = await session.execute(
            select(User)
            .options(joinedload(User.friends))  # Подгружаем друзей вместе с пользователем
            .where(User.id_telegram == id_telegram)
    )
    user = result.scalars().first()

    if user is None:
        return None

    friends_list = []
    for friend in user.friends:
        friends_list.append({
                'username': friend.user_name,
                'count_coins': friend.count_coins,
                'level': friend.level
        })

    return friends_list


async def get_transactions_by_id(id_telegram: int, limit: int, offset: int, session) -> List[HistoryTransaction]:
    """
    Получить список всех транзакций пользователя с заданным id_telegram.
    :param id_telegram: int
    :param session: async_session
    :return: HistoryTransaction
    """
    user = await session.execute(
            select(User).where(User.id_telegram == id_telegram)
    )
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await session.execute(
            select(HistoryTransaction)
            .where(HistoryTransaction.user_id == user.id)
            .order_by(HistoryTransaction.transaction_date.desc())
            .limit(limit)
            .offset(offset)
    )
    transactions = result.scalars().all()
    return transactions


async def get_users_limit(limit: int, offset: int, session) -> List[dict]:
    """
    Получить список всех пользователей
    :param limit:
    :return:
    """
    result = await session.execute(
            select(User.id_telegram, User.user_name, User.count_coins)
            .limit(limit)
            .offset(offset)
            .order_by(User.count_coins.desc())
    )
    users = result.fetchall()
    users_list = [
            dict(id_telegram=row[0], user_name=row[1], count_coins=row[2])
            for row in users
    ]

    return users_list
