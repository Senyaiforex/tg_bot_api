from sqlalchemy import select, func, case
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
                            Post.url_message_main == url_message,
                            Post.url_message_free == url_message)
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
    async def get_count_posts_with_type(cls, session: async_session,
                                         date: date, method: str) -> list[int]:
        """
        Метод для получения количества опубликованных постов по временному интервалу
        по типам публикации
        :param session: Асинхронная сессия
        :param date: Дата
        :return: Количество постов
        :rtype: list[int
        """
        count_for_method = await session.execute(
                select(func.count(Post.id))
                .where(
                        and_(
                                Post.date_public == date,
                                Post.method == method
                        )
                ))
        return count_for_method.scalar()

    @classmethod
    async def get_posts_by_celery(cls, session: async_session, today: date) -> int:
        """
        Метод для получения всех опубликованных постов в базе данных
        :param session: Асинхронная сессия
        :return: количество постов
        :rtype: int
        """
        query_posts = await session.execute(
                select(Post)
                .where(and_(
                        Post.active == True,
                        Post.date_expired < today
                )
                )
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
    async def update_liquid_posts(cls, session: async_session,
                                  dict_param_liquid: dict[str, int]) -> None:
        """
        Обновить параметры пула ликвидности дял публикаций постов
        :param session: Асинхронная сессия
        :param kwargs: Параметры ликвидности
        :return:
        """
        stmt = (
                update(LiquidPosts).
                where(LiquidPosts.id == 1).
                values(**dict_param_liquid)
        )
        await session.execute(stmt)
        await session.commit()

    from sqlalchemy import update

    @classmethod
    async def increment_liquid_posts(cls, session: async_session, dict_param_liquid: dict[str, int]) -> None:
        """
        Увеличить параметры пула ликвидности для публикаций постов
        :param session: Асинхронная сессия
        :param dict_param_liquid: Параметры ликвидности для увеличения
        :return: None
        """
        # Получаем текущий экземпляр
        liquid_post = await session.get(LiquidPosts, 1)
        for key, value in dict_param_liquid.items():
            if hasattr(liquid_post, key):
                setattr(liquid_post, key, getattr(liquid_post, key) + value)

        # Сохраняем изменения
        session.add(liquid_post)
        await session.commit()

    @classmethod
    async def liquid_clear(cls, session):
        """
        Очистить пул ликвидности
        :param session: Асинхронная сессия
        :return: None
        """
        stmt = update(LiquidPosts).where(LiquidPosts.id == 1).values(
                current_coins=0, current_token=0,
                current_free=0, current_money=0,
                current_stars=0
        )
        await session.execute(stmt)
        await session.commit()