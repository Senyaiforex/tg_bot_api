from typing import List, Dict, Union
from sqlalchemy import func
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, aliased, selectinload
from models import User, HistoryTransaction, SearchPost, Post
from datetime import date, timedelta
from database import async_session


class UserRepository:
    @classmethod
    async def get_user_by_telegram_id(cls, telegram_id: int, session: async_session) -> User:
        """
        Функция для получения пользователя из базы данных по id_telegram
        Если пользователь отсутствует в БД, то вернёт 404
        :param telegram_id: айди пользователя телеграм
        :param session: асинхронная сессия
        :return: инстанс пользователя
        :rtype: User
        """
        result = await session.execute(
                select(User)
                .options(joinedload(User.rank))
                .where(User.id_telegram == telegram_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @classmethod
    async def get_user_with_tasks(cls, telegram_id: int, session: async_session) -> User:
        """
        Функция для получения пользователя из базы данных по id_telegram вместе с выполненными задачами
        Если пользователь отсутствует в БД, то вернёт 404
        :param telegram_id: айди пользователя телеграм
        :param session: асинхронная сессия
        :return: инстанс пользователя
        :rtype: User
        """
        result = await session.execute(
                select(User)
                .options(selectinload(User.tasks))
                .where(User.id_telegram == telegram_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @classmethod
    async def get_user_by_username(cls, username: str, session: async_session) -> User:
        """
        Функция дял получения пользователя из базы данных по его юзернейму
        Если пользователь отсутствует в БД, то вернёт 404
        :param username: юзернейм пользователя телеграмм
        :param session: асинхронная сессия
        :return: Инстанс пользователя
        :rtype: User
        """
        result = await session.execute(
                select(User)
                .options(selectinload(User.friends))
                .options(selectinload(User.tasks))
                .options(selectinload(User.history_transactions))
                .options(selectinload(User.posts))
                .options(joinedload(User.rank))
                .where(User.user_name == username)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @classmethod
    async def get_user_tg(cls, telegram_id: int, session: async_session) -> User:
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

    @classmethod
    async def get_admins(cls, session: async_session) -> list[User]:
        """
        Метод для получения всех пользователей с user.admin == True
        из базы данных
        :param session: Асинхронная сессия
        :return: список пользователей
        :rtype: list[User]
        """
        result = await session.execute(
                select(User)
                .where(User.admin == True)
        )
        admins = result.scalars().all()
        return admins

    @classmethod
    async def create_user_admin(cls, telegram_id: int, username: str, session: async_session) -> None:
        """
        Функция для создания нового пользователя-администратора в базе данных
        :param telegram_id: Айди пользователя телеграмм
        :param username: Никнейм пользователя
        :param session: Асинхронная сессия
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

    @classmethod
    async def base_create_user(cls, user, session: async_session) -> User:
        """
        Функция для создания нового пользователя в базе данных
        :param user: User
        :param session:
        :return: Инстанс пользователя
        :rtype: User
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

    @classmethod
    async def get_count_coins(cls, session: async_session, id_telegram: int) -> int:
        """
        Метод для получения количество монет у пользователя по его айди телеграмм
        :param session: Асинхронная сессия
        :param id_telegram: Айди телеграм пользователя
        :return: Количество монет
        :rtype: int
        """
        result_user = await session.execute(
                select(User)
                .where(User.id_telegram == id_telegram)
        )
        user = result_user.scalars().first()
        return user.count_coins

    @classmethod
    async def change_coins_by_id(cls, id_telegram: int,
                                 amount: int, add: bool, description: str, session: async_session) -> User:
        """
        Функция для изменения количества токенов у пользователя
        :param id_telegram: айди телеграм пользователя
        :param amount: количество для изменения
        :param add: если add=True, то прибавить, если False, то вычесть из текущего количества
        :param description: Описание транзакции
        :param session: Асинхронная сессия
        :return: Инстанс пользователя
        :rtype: User
        """
        user = await cls.get_user_by_telegram_id(id_telegram, session)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if add:
            description = description
            await user.update_count_coins(session, amount, description)
        else:
            user.count_coins -= amount
            await session.commit()
        return user

    @classmethod
    async def change_pharmd_by_id(cls, id_telegram: int, amount: int,
                                  add: bool, session: async_session) -> User:
        """
        Функция для изменения количества фарма у пользователя
        :param id_telegram: айди телеграм пользователя
        :param amount: количество для изменения
        :param add: если add=True, то прибавить, если False, то вычесть из текущего количества
        :param session: Асинхронная сессия
        :return: Инстанс пользователя
        :rtype: User
        """
        user = await cls.get_user_by_telegram_id(id_telegram, session)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if add:
            user.count_pharmd += amount
        else:
            user.count_pharmd -= amount
        await session.commit()
        return user

    @classmethod
    async def change_spinners_by_id(cls, id_telegram: int, amount: int,
                                    add: bool, session: async_session) -> User:
        """
        Функция для изменения количества спиннеров у пользователя
        :param id_telegram: айди телеграм пользователя
        :param amount: количество для изменения
        :param add: если add=True, то прибавить, если False, то вычесть из текущего количества
        :param session: Асинхронная сессия
        :return: Инстанс пользователя
        :rtype: User
        """
        user = await cls.get_user_by_telegram_id(id_telegram, session)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if add:
            user.spinners += amount
        else:
            user.spinners -= amount
        await session.commit()
        return user

    @classmethod
    async def create_user_tg(cls, id_telegram: int, username: str, session: async_session) -> None:
        """
        Функция для создания нового пользователя в базе данных из телеграмм бота.
        :param id_telegram: Айди телеграм пользователя
        :param username: Никнейм пользователя
        :param session: Асинхронная сессия
        :return: None
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

    @classmethod
    async def get_friends(cls, id_telegram: int, session: async_session) -> List[Dict[str, Union[int, str]]] | None:
        """
        Получить список друзей пользователя с заданным id_telegram.
        Если такого пользователя не существует, вернёт None
        Если друзей нет, то вернёт пустой список
        :param id_telegram: ID пользователя в Telegram.
        :param session: Асинхронная сессия
        :return: Список друзей с их username, count_coins и level.
        """
        # Находим пользователя по id_telegram
        result = await session.execute(
                select(User)
                .options(selectinload(User.friends).selectinload(User.rank))
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
                    'level': friend.rank.level if friend.rank else None,
                    'rank': friend.rank.rank.name if friend.rank else None,
                    'date_registration': friend.registration_date.strftime('%d-%m-%Y')
            })

        return friends_list

    @classmethod
    async def get_transactions_by_id(cls, id_telegram: int, limit: int, offset: int,
                                     session: async_session) -> List[HistoryTransaction]:
        """
        Получить все транзакции пользователя по его id_telegram
        Если такой пользователь не найден, вернёт 404
        :param id_telegram: Айди телеграм пользователя
        :param limit: Максимальное количество
        :param offset: Параметр пагинации
        :param session: Асинхронная сессия
        :return: Список транзакций
        :rtype: list[HistoryTransaction]
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

    @classmethod
    async def get_users_limit(cls, limit: int, offset: int, session: async_session) -> List[dict]:
        """
        Получить список всех пользователей из базы данных
        :param limit: Максимальное количество
        :param offset: Параметр пагинации
        :param session: Асинхронная сессия
        :return: Список словарей с данными пользователей
        :rtype: list[dict]
        """
        result = await session.execute(
                select(User.id_telegram, User.user_name, User.total_coins)
                .limit(limit)
                .offset(offset)
                .order_by(User.total_coins.desc())
        )
        users = result.fetchall()
        users_list = [
                dict(id_telegram=row[0], user_name=row[1], total_coins=row[2])
                for row in users
        ]

        return users_list

    @classmethod
    async def get_count_users(cls, session: async_session) -> int:
        """
        Функция для получения общего количества пользователей в базе данных
        :param session: Асинхронная сессия
        :return: Количество пользователей
        :rtype: int
        """
        count_users = await session.execute(
                select(func.count(User.id))
                .where(User.active == True)
        )
        return count_users.scalar()

    @classmethod
    async def get_count_admins(cls, session: async_session) -> int:
        """
        Функция для получения общего количества администраторов в базе данных
        :param session: Асинхронная сессия
        :return: Количество пользователей user с user.admin == True
        :rtype: int
        """
        count_admins = await session.execute(
                select(func.count(User.id))
                .where(User.admin == True)
        )
        return count_admins.scalar()

    @classmethod
    async def get_users_date(cls, session: async_session, date: date) -> tuple[int]:
        """
        Функция для получения количества зарегистрированных пользователей в базе данных
        за сегодняшний день, неделю, месяц
        :param session: Асинхронная сессия
        :param date: Дата
        :return: Количество пользователей
        :rtype: tuple[int]
        """
        week_date = date - timedelta(days=7)
        month_date = date - timedelta(days=30)
        count_today = await session.execute(
                select(func.count(User.id))
                .where(User.registration_date == date)
        )
        count_week = await session.execute(
                select(func.count(User.id))
                .where(User.registration_date >= week_date)
        )
        count_month = await session.execute(
                select(func.count(User.id))
                .where(User.registration_date >= month_date)
        )
        return (count_today.scalar(), count_week.scalar(), count_month.scalar())

    @classmethod
    async def block_user(cls, username: str, session: async_session) -> None:
        """
        Заблокировать пользователя в базе данных с переданным никнеймом
        Если такого пользователя в базе данных не существует, вернёт 404
        :param username: Никнейм пользователя
        :param session: Асинхронная сессия
        :return: None
        """
        user = await session.execute(
                select(User).where(User.user_name == username)
        )
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.active = False
        await session.commit()

    @classmethod
    async def get_users_with_posts_count(cls, session: async_session) -> list[User]:
        """
        Метод для получения всех пользователей с их постами, у которых
        количество опубликованных постов больше 0
        :param session: Асинхронная сессия
        :return: Список пользователей
        :rtype: User
        """
        post_alias = aliased(Post)  # Создаем алиас для таблицы Post

        subquery = (
                select(
                        User.id_telegram.label('user_telegram'),  # Выбираем поле user_telegram
                        func.count(post_alias.id).label("post_count")  # Считаем количество постов
                )
                .join(post_alias, User.id_telegram == post_alias.user_telegram, isouter=True)  # Левое соединение с Post
                .group_by(User.id_telegram)  # Группируем по полю user_telegram
                .subquery()
        )
        stmt = (
                select(func.count())
                .select_from(subquery)
                .where(subquery.c.post_count > 0)
        )

        result = await session.execute(stmt)
        users_with_posts_count = result.scalar()
        return users_with_posts_count

    @classmethod
    async def get_users_with_search(cls, session: async_session) -> list[User]:
        """
        Метод для получения пользователей вместе с его листом ожидания товаров
        :param session: Асинхронная сессия
        :return: Список пользователей
        :rtype: list[User]
        """
        query_users = await session.execute(
                select(User)
                .options(selectinload(User.search_posts))
        )
        users = query_users.unique().scalars().all()
        return users


class SearchListRepository:
    @classmethod
    async def get_search_all(cls, session: async_session) -> list[SearchPost]:
        """
        Метод для получения всех листов ожидания из базы
        :param session: Асинхронная сессия
        :return: список листов ожидания
        :rtype: list[SearchPost]
        """
        result_search = await session.execute(
                select(SearchPost)
        )
        search_posts = result_search.scalars().unique().all()
        return search_posts

    @classmethod
    async def create_search(cls, session: async_session, id_telegram: int, name: str) -> bool:
        """
        Создание товара в листе ожидания пользователя
        Если у пользователя уже есть 10(maximum) товаров в листе ожидания, то вернёт False,
        тогда пользователю необходимо удалить товары из листа ожидания
        :param session: Асинхронная сессия
        :param id_telegram: Айди телеграм пользователя
        :param name: Наименования товара для добавления в лист ожидания
        :return: bool
        """
        result_user = await session.execute(
                select(User)
                .options(selectinload(User.search_posts))
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

    @classmethod
    async def get_search_by_user(cls, session: async_session, telegram_id: int) -> list[SearchPost]:
        """
        Метод для получения товаров из листа ожидания у пользователя по его
        id_telegram
        :param session: Асинхронная сессия
        :param telegram_id: Айди телеграмм
        :return: Пользователь с его листом ожидания
        :rtype: User
        """
        query_user = await session.execute(
                select(User)
                .options(selectinload(User.search_posts))
                .where(User.id_telegram == telegram_id)
        )
        user = query_user.scalars().first()
        return user.search_posts

    @classmethod
    async def search_delete(cls, session: async_session, search_id: int | str) -> None:
        """
        Удалить товар из листа ожидания по его search_id
        :param session: Асинхронная сессия
        :param search_id: ID товара в листе ожидания в БД
        :return: None
        """
        query = delete(SearchPost).where(SearchPost.id == search_id)
        await session.execute(query)
        await session.commit()
