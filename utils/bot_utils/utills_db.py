from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, friends
from repository import get_count_users, get_count_admins, get_users_today, get_posts_all, get_user_by_telegram_id, \
    get_user_by_username, get_transactions_by_id, get_friends, block_user
from fastapi import HTTPException

async def get_user_bot(telegram_id: int, session: AsyncSession):
    """
    Функция дял получения пользователя из базы данных по id_telegram
    :param telegram_id:
    :param session:
    :return:
    """
    result = await session.execute(select(User).where(User.id_telegram == telegram_id))
    user = result.scalars().first()
    return user


async def handle_invitation(inviter_id: int, user_id: int, username: str, session: AsyncSession) -> None:
    """
     Функция обработки приглашения пользователя
    :param inviter_id: id пользователя, который пригласил.
    :param user_id: id пользователя, который получил приглашение.
    :return:
    """

    inviter = await session.execute(select(User).where(User.id_telegram == inviter_id))
    inviter = inviter.scalars().first()
    query = await session.execute(select(User).filter(User.id_telegram == user_id))
    user = query.scalars().one_or_none()
    if user:
        return
    await inviter.update_count_coins(session, 5000, f"Приглашение друга")
    inviter.count_invited_friends += 1
    new_user = User(id_telegram=user_id,
                    user_name=username)
    await new_user.update_count_coins(session, 5000, f"Бонус за регистрацию", new=True)
    session.add(new_user)
    await session.execute(friends.insert().values(
            friend1_id_telegram=inviter_id,
            friend2_id_telegram=user_id
    ))
    await session.commit()



async def get_info_users(session: AsyncSession) -> dict[str: int]:
    """
    Функция для получения информации по статистике пользователей
    :param session:
    :return:
    """
    dict_info = {}
    count_users, count_admins = (await get_count_users(session),
                                 await get_count_admins(session))
    count_users_today = await get_users_today(session)
    count_posts = await get_posts_all(session)
    dict_info['Количество активных пользователей'] = count_users
    dict_info['Новых пользователей сегодня'] = count_users_today
    dict_info['Количество администраторов'] = count_admins
    dict_info['Общее количество размещённых постов'] = count_posts
    return dict_info

async def get_info_from_user(username: str, session: AsyncSession) -> dict[str: int | str]:
    """
    Функция для получения информации о пользователе по его telegram_id
    :param telegram_id:
    :param session:
    :return:
    """
    dict_info = {}
    try:
        user = await get_user_by_username(username, session)
    except HTTPException as e:
        return dict_info
    dict_info = {
            'Телеграм id пользователя': user.id_telegram,
            'Никнейм': user.user_name,
            'Дата регистрации': user.registration_date.strftime('%d-%m-%Y'),
            'Количество токенов': user.count_coins,
            'Количество фарма': user.count_pharmd,
            'Уровень': user.level,
            'Количество приглашенных друзей': user.count_invited_friends,
            'Количество покупок': user.purchase_count,
            'Количество продаж': user.sale_count,
            'Количество размещённых постов': len(user.posts),
            'Количество транзакций': len(user.history_transactions),
            'Количество выполненных задач': len(user.tasks),
            'Активный': 'Да' if user.active else 'Нет'
    }
    return dict_info

async def get_all_transactions(telegram_id: int, session) -> list:
    """
    Функция для получения всех транзакций пользователя по его telegram_id
    :param telegram_id:
    :param session:
    :return:
    """
    list_info = []
    try:
        transactions = await get_transactions_by_id(telegram_id, 100, 0, session)
    except HTTPException as e:
        return list_info
    for transaction in transactions:
        list_info.append({
                'Дата': transaction.transaction_date.strftime('%d-%m-%Y'),
                'Описание': transaction.description,
                'Сумма': transaction.change_amount
        })
    return list_info

async def get_friends_by_user(telegram_id: int, session: AsyncSession) -> dict:
    """
    Функция для получения всех друзей пользователя в виде словаря
    :param telegram_id:
    :param session:
    :return:
    """
    friends = await get_friends(telegram_id, session)
    return friends


async def block_user_by_username(username: str, session: AsyncSession) -> bool:
    """
    Функция для блокировки пользователя по его никнейму
    :param username:
    :param session:
    :return:
    """
    try:
        await block_user(username, session)
        return True
    except HTTPException as e:
        return False