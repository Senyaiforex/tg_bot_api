from typing import List, Dict, Union, Any

from fastapi import HTTPException

from app.schemes import HistoryTransactionList
from database import async_session
from .schemes import UserIn
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from .models import User, HistoryTransaction


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


async def base_create_user(user: UserIn, session: async_session) -> User:
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


async def get_transactions_by_id(id_telegram: int, limit: int, session) -> List[HistoryTransaction]:
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
    )
    transactions = result.scalars().all()
    return transactions
