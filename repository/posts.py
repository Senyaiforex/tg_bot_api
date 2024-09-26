from sqlalchemy import select, func
from database import async_session
from sqlalchemy import select, delete, update, or_, and_
from models import Post, LiquidPosts
from datetime import date, timedelta


class PostRepository:
    @classmethod
    async def get_posts_all(cls, session: async_session) -> int:
        """
        Метод для получения общего количества постов в базе данных
        :param session: Асинхронная сессия
        :return: Количество постов
        :rtype: int
        """
        count_posts = await session.execute(
                select(func.count(Post.id))
        )
        return count_posts.scalar()

    @classmethod
    async def create_post(cls, session: async_session, **kwargs) -> Post:
        """
        Метод для создания поста в базе данных
        :param session: Асинхронная сессия
        :param kwargs: Именованные аргументы для создания поста
        :return:
        """
        marketplace = kwargs.pop('marketplace', 'Нет')
        new_post = Post(
                marketplace=marketplace,
                **kwargs
        )
        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)
        return new_post

    @classmethod
    async def update_post(cls, session: async_session, post_id: int | str, **kwargs) -> None:
        """
        Метод для обновления параметров поста с заданным post_id
        :param session: Асинхронная сессия
        :param post_id: ID поста в БД
        :param kwargs: именованные аргументы
        :return: инстанс поста
        :rtype: Post
        """
        stmt = (
                update(Post).
                where(Post.id == post_id).
                values(kwargs)
        )
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_posts_by_user(cls, session: async_session, id_telegram: int) -> list[Post]:
        """
        Метод для получения всех постов, опубликованным пользователем по
        его айди телеграм
        :param session: Асинхронная сессия
        :param id_telegram: Айди телеграм
        :return: Список постов
        :rtype: list[Post]
        """
        result = await session.execute(
                select(Post)
                .where(Post.user_telegram == id_telegram)
        )
        posts = result.scalars().all()
        return posts

    @classmethod
    async def post_delete(cls, session: async_session, post_id: int | str) -> None:
        """
        Метод для удаления поста с заданным post_id
        :param session: Асинхронная сессия
        :param post_id: ID поста из БД
        :return: None
        """
        query = delete(Post).where(Post.id == post_id)
        await session.execute(query)
        await session.commit()

    @classmethod
    async def get_post(cls, session: async_session, post_id: int | str) -> Post:
        """
        Метод для получения поста по его post_id
        :param session: Асинхронная сессия
        :param post_id: ID поста из БД
        :return: Инстанс поста
        :rtype: Post
        """
        result = await session.execute(
                select(Post).where(Post.id == post_id)
        )
        post = result.scalars().first()
        return post

    @classmethod
    async def get_post_by_url(cls, session: async_session, url_message: str) -> Post:
        """
        Метод для получения поста по url сообщения, в котором он размещён в группе
        :param session: Асинхронная сессия
        :param url_message: ссылка на сообщение
        :return: инстанс поста
        :rtype: Post
        """
        result = await session.execute(
                select(Post).where(
                        or_(Post.url_message == url_message,
                            Post.url_message_main == url_message)
                )
        )
        post = result.scalars().first()
        return post

    @classmethod
    async def get_count_post_by_time(cls, session: async_session, date: date) -> list[int]:
        """
        Метод для получения количество опубликованных постов:
            * За сегодня
            * За неделю
            * За месяц
        :param session: Асинхронная сессия
        :param date: Дата
        :return: Количество постов
        :rtype: list[int]
        """
        count_today = await session.execute(
                select(func.count(Post.id))
                .where(Post.date_public == date)
        )
        week_date = date - timedelta(days=7)
        month_date = date - timedelta(days=30)
        count_week = await session.execute(
                select(func.count(Post.id))
                .where(Post.date_public >= week_date)
        )
        count_month = await session.execute(
                select(func.count(Post.id))
                .where(Post.date_public >= month_date)
        )
        list_count = [count_today.scalar(), count_week.scalar(), count_month.scalar()]
        return list_count

    @classmethod
    async def get_count_posts_with_types(cls, session: async_session,
                                         date: date, type_date: str) -> list[int]:
        """
        Метод для получения количества опубликованных постов по временному интервалу
        по типам публикации
        :param session: Асинхронная сессия
        :param date: Дата
        :param type_date: Тип(за сегодня, за неделю, за месяц)
        :return: Количество постов
        :rtype: list[int
        """
        date_dict = {"today": date,
                     'week': date - timedelta(days=7),
                     'month': date - timedelta(days=30)}
        date = date_dict[type_date]
        count_free = await session.execute(
                select(func.count(Post.id))
                .where(
                        and_(
                                Post.date_public >= date,
                                Post.method == 'free'
                        )
                ))
        count_coins = await session.execute(
                select(func.count(Post.id))
                .where(
                        and_(
                                Post.date_public >= date,
                                Post.method == 'coins'
                        )
                ))
        count_token = await session.execute(
                select(func.count(Post.id))
                .where(
                        and_(
                                Post.date_public >= date,
                                Post.method == 'token'
                        )
                ))
        count_money = await session.execute(
                select(func.count(Post.id))
                .where(
                        and_(
                                Post.date_public >= date,
                                Post.method == 'money'
                        )
                ))
        counts_posts = [count_free.scalar(), count_token.scalar(),
                        count_coins.scalar(), count_money.scalar()]
        return counts_posts

    @classmethod
    async def get_posts_by_celery(cls, session: async_session) -> int:
        """
        Метод для получения всех опубликованных постов в базе данных
        :param session: Асинхронная сессия
        :return: количество постов
        :rtype: int
        """
        query_posts = await session.execute(
                select(Post)
                .where(Post.active == True)
        )
        posts_all = query_posts.scalars().all()
        return posts_all

    @classmethod
    async def post_update_by_celery(cls, session: async_session, post_id: int, **kwargs) -> None:
        """
        Метод для обновления параметров поста в БД
        :param session: Асинхронная сессия
        :param post_id: ID поста в БД
        :param kwargs: Параметры, которые нужно обновить
        :return: None
        """
        stmt = (
                update(Post).
                where(Post.id == post_id).
                values(kwargs)
        )
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_liquid_posts(cls, session: async_session) -> LiquidPosts:
        """
        Метод для получения информации об установленной ликвидности
        :param session: Асинхронная сессия
        :return: Инстанс ликвидности
        :rtype: LiquidPosts
        """
        result = await session.execute(
                select(LiquidPosts)
        )
        liquid_posts = result.scalar_one_or_none()
        return liquid_posts

    @classmethod
    async def update_liquid_posts(cls, session: async_session, **kwargs) -> None:
        """
        Обновить параметры пула ликвидности дял публикаций постов
        :param session: Асинхронная сессия
        :param kwargs: Параметры ликвидности
        :return:
        """
        stmt = (
                update(LiquidPosts).
                where(LiquidPosts.id == 1).
                values(kwargs)
        )
        await session.execute(stmt)
        await session.commit()