from fastapi import HTTPException
import models
from sqlalchemy.future import select
from database import async_session
import schemes


async def get_user_by_telegram_id(telegram_id: int, session: async_session):
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


async def base_create_user(user: schemes.UserIn, session: async_session):
    """
    Функция для создания нового пользователя в базе данных
    :param user:
    :param session:
    :return:
    """
    new_user = models.User(
            id_telegram=user.id_telegram,
            user_name=user.user_name,
            count_coins=user.count_coins,
            count_pharmd=user.count_pharmd
    )
    result = await session.execute(select(models.User). \
                                   where(models.User.id_telegram == new_user.id_telegram))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def change_tokens_by_id(
        id_telegram: int,
        amount: int,
        add: bool,
        session: async_session
):
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
        user.count_coins += amount
    else:
        user.count_coins -= amount
    await session.commit()
    return user


async def change_pharmd_by_id(
        id_telegram: int,
        amount: int,
        add: bool,
        session: async_session
):
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
    new_user = models.User(
            id_telegram=id_telegram,
            user_name=username,
    )
    result = await session.execute(select(models.User). \
                                   where(models.User.id_telegram == new_user.id_telegram))
    user = result.scalars().first()
    if user:
        return
    else:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)


from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models import User


async def get_friends(id_telegram: int, session):
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
        print(friend.user_name)
        friends_list.append({
                'username': friend.user_name,
                'count_coins': friend.count_coins,
                'level': friend.level
        })

    return friends_list
