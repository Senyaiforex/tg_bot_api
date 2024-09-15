from typing import List, Dict, Union
from sqlalchemy import select, func
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bot.bot_main import marketplace
from database import async_session
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
from models import User, HistoryTransaction, Task, Post, Pull, SearchPost
from datetime import date, datetime, timedelta


async def get_user_by_telegram_id(telegram_id: int, session: async_session) -> User:
    """
    Функция дял получения пользователя из базы данных по id_telegram
    :param telegram_id:
    :param session:
    :return:
    """
    result = await session.execute(
            select(User)
            .options(joinedload(User.friends))
            .options(joinedload(User.tasks))
            .where(User.id_telegram == telegram_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_by_username(username: str, session: async_session) -> User:
    """
    Функция дял получения пользователя из базы данных по id_telegram
    :param username:
    :param session:
    :return:
    """
    result = await session.execute(
            select(User)
            .options(joinedload(User.friends))
            .options(joinedload(User.tasks))
            .options(joinedload(User.history_transactions))
            .options(joinedload(User.posts))
            .where(User.user_name == username)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_tg(telegram_id: int, session: async_session) -> User:
    """
    Функция дял получения пользователя из базы данных по id_telegram
    :param telegram_id:
    :param session:
    :return:
    """
    result = await session.execute(
            select(User)
            .where(User.id_telegram == telegram_id)
    )
    user = result.scalars().first()
    return user


async def create_user_admin(telegram_id: int, username: str, session: async_session) -> User:
    """
    Функция для создания нового пользователя в базе данных
    :param user:
    :param session:
    :return:
    """
    new_user = User(
            id_telegram=telegram_id,
            user_name=username,
            admin=True
    )
    result = await session.execute(select(User). \
                                   where(User.id_telegram == new_user.id_telegram))
    user = result.scalars().first()
    if user:
        user.admin = True
    else:
        session.add(new_user)
    await session.commit()


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


async def create_task(url: str, description: str, type_task: str, date: str, session: async_session) -> bool:
    """
    Функция для создания новой задачи в базе данных
    :param url:
    :param description:
    :param type_task:
    :return:
    """
    new_task = Task(
            url=url,
            description=description,
            type_task=type_task,
            date_limit=datetime.strptime(date, '%d.%m.%Y')
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


async def get_all_tasks(session) -> list[Task]:
    today = datetime.today()
    result = await session.execute(
            select(Task)
            .where(Task.date_limit >= today)
    )
    tasks = result.scalars().all()
    return tasks


async def change_coins_by_id(
        id_telegram: int,
        amount: int,
        add: bool,
        description,
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
        description = description
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


async def change_spinners_by_id(
        id_telegram: int,
        amount: int,
        add: bool,
        session: async_session
) -> User:
    """
    Функция для изменения количества спиннеров у пользователя
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
        user.spinners += amount
    else:
        user.spinners -= amount
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
    result = await session.execute(select(User)
                                   .where(User.id_telegram == new_user.id_telegram))
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
            .options(joinedload(User.friends))
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
                'level': friend.level,
                'date_registration': friend.registration_date.strftime('%d-%m-%Y')
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


async def get_count_users(session) -> int:
    """
    Функция для получения общего количества пользователей в базе данных
    :param session:
    :return:
    """
    count_users = await session.execute(
            select(func.count(User.id))
            .where(User.active == True)
    )
    return count_users.scalar()


async def get_count_admins(session) -> int:
    """
    Функция для получения общего количества администраторов в базе данных
    :param session:
    :return:
    """
    count_admins = await session.execute(
            select(func.count(User.id))
            .where(User.admin == True)
    )
    return count_admins.scalar()


async def get_users_today(session) -> int:
    """
    Функция для получения количества пользователей за сегодняшний день
    :param session:
    :return:
    """
    today = date.today()
    count_users_today = await session.execute(
            select(func.count(User.id))
            .where(User.registration_date == today)
    )
    return count_users_today.scalar()


async def get_posts_all(session) -> int:
    """
    Функция для получения общего количества постов в базе данных
    :param session:
    :return:
    """
    count_posts = await session.execute(
            select(func.count(Post.id))
    )
    return count_posts.scalar()


async def block_user(username: str, session):
    """
    Функция для блокировки пользователя
    :param session:
    :return:
    """
    user = await session.execute(
            select(User).where(User.user_name == username)
    )
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.active = False
    await session.commit()


async def get_pull(session):
    """
    Функция для получения пула
    :param session:
    :return:
    """
    pull = await session.execute(
            select(Pull)
    )
    return pull.scalars().first()


async def set_pull_size(dict_pull_sizes, session):
    pull_query = await session.execute(select(Pull))
    pull = pull_query.scalars().first()
    if not pull:
        pull = Pull(
                farming=dict_pull_sizes['farming'],
                friends=dict_pull_sizes['friends'],
                task=dict_pull_sizes['task'],
                plan=dict_pull_sizes['plan'],
                coins=dict_pull_sizes['coins']
        )
        session.add(pull)
    else:
        for key, value in dict_pull_sizes.items():
            setattr(pull, key, value)

    await session.commit()


async def create_post(session, **kwargs):
    new_post = Post(
            **kwargs
    )
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post


async def get_users_with_search(session):
    query_users = await session.execute(
            select(User)
            .options(joinedload(User.search_posts))
    )
    users = query_users.unique().scalars().all()
    return users


async def get_search_all(session):
    result_search = await session.execute(
            select(SearchPost)
    )
    search_posts = result_search.scalars().unique().all()
    return search_posts


async def create_search(session, id_telegram, name) -> bool:
    result_user = await session.execute(
            select(User)
            .options(joinedload(User.search_posts))
            .where(User.id_telegram == id_telegram)
    )
    user = result_user.scalars().first()
    new_search = SearchPost(name=name)
    user_search = user.search_posts
    if len(user_search) >= 10:
        return False
    else:
        session.add(new_search)
        user_search.append(new_search)
        await session.commit()
        return True


async def get_count_coins(session, id_telegram: int) -> int:
    result_user = await session.execute(
            select(User)
            .where(User.id_telegram == id_telegram)
    )
    user = result_user.scalars().first()
    return user.count_coins


async def update_post(session, post_id, **kwargs):
    post = await session.execute(
            select(Post)
            .where(Post.id == post_id)
    )
    post = post.scalars().first()
    for key, value in kwargs.items():
        setattr(post, key, value)

    await session.commit()
    await session.refresh(post)
    return post


async def get_search_by_user(session, telegram_id):
    query_user = await session.execute(
            select(User)
            .options(joinedload(User.search_posts))
            .where(User.id_telegram == telegram_id)
    )
    user = query_user.scalars().first()
    return user.search_posts


async def search_delete(session, search_id) -> None:
    query = delete(SearchPost).where(SearchPost.id == search_id)
    await session.execute(query)
    await session.commit()


async def get_posts_by_user(session, user_id) -> list[Post]:
    result = await session.execute(
            select(Post)
            .where(Post.user_telegram == user_id)
    )
    posts = result.scalars().all()
    return posts


async def post_delete(session, post_id) -> None:
    query = delete(Post).where(Post.id == post_id)
    await session.execute(query)
    await session.commit()


async def get_post(session, post_id) -> Post:
    result = await session.execute(
            select(Post).where(Post.id == post_id)
    )
    post = result.scalars().first()
    return post


async def post_update(session, post_id, **kwargs) -> None:
    stmt = (
            update(Post).
            where(Post.id == post_id).
            values(kwargs)
    )
    await session.execute(stmt)
    await session.commit()


async def get_post_by_url(session, url_message: str) -> Post:
    result = await session.execute(
            select(Post).where(Post.url_message == url_message)
    )
    post = result.scalars().first()
    return post


async def get_count_post_by_time(session: AsyncSession,
                                 date: date) -> tuple[int]:
    count_today = await session.execute(
            select(func.count(Post.id))
            .where(Post.public_date == date)
    )
    week_date = date - timedelta(days=7)
    month_date = date - timedelta(days=30)
    count_week = await session.execute(
            select(func.count(Post.id))
            .where(Post.public_date >= week_date)
    )
    count_month = await session.execute(
            select(func.count(Post.id))
            .where(Post.public_date >= month_date)
    )
    return tuple(count_today.scalar(),
                 count_week.scalar(),
                 count_month.scalar())
