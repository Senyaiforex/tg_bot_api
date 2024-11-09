from sqlalchemy import select, update, delete, func
from models import CountSellers
from database import async_session


class SellerRepository:
    @classmethod
    async def create_instance_seller(cls, session: async_session, count_subscribes, date):
        """
        Метод для создания нового экземпляра продавцов и пользователей
        :param session: Асинхронная сессия
        :param date: Дата
        :param count_subscribes: Количество подписчиков
        :return: None
        """
        serller_instance = CountSellers(created_at=date,
                                        count=0, subscribes_count=count_subscribes)
        session.add(serller_instance)
        await session.commit()
    @classmethod
    async def get_count_sellers(cls, session: async_session, date) -> int:
        """
        Метод для получения количества продавцов за сегодня
        :param session: Асинхронная сессия
        :param date: Дата
        :rtype: int
        """
        stmt = select(CountSellers.count).where(CountSellers.created_at == date)
        result = await session.execute(stmt)
        count = result.scalar_one_or_none()
        return count if count else 0

    @classmethod
    async def get_count_users(cls, session: async_session, date) -> int:
        """
        Метод для получения количества подписчиков в группе
        :param session: Асинхронная сессия
        :rtype: int
        :date: Дата
        """
        stmt = select(CountSellers.subscribes_count).where(CountSellers.created_at == date)
        result = await session.execute(stmt)
        count = result.scalar_one_or_none()
        return count if count else 0

    @classmethod
    async def seller_add(cls, session: async_session, date) -> None:
        """
        Метод для увеличения количества продавцов в БД
        :param session: Асинхронная сессия
        :param date: Дата
        :return: None
        """
        stmt = (
                update(CountSellers).
                where(CountSellers.created_at == date).
                values(count=CountSellers.count + 1)
        )

        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def sellers_clear(cls, date, session: async_session) -> None:
        """
        Метод для очистки количества продавцов в БД
        :param date: Дата
        :param session: Асинхронная сессия
        :return: None
        """
        stmt = (
                delete(CountSellers).
                where(CountSellers.created_at <= date)
        )

        await session.execute(stmt)
        await session.commit()
    @classmethod
    async def count_all_sellers(cls, session: async_session) -> int:
        """
        Получить количество всех продавцов
        :param session:
        :return:
        """
        stmt = select(func.sum(CountSellers.count))
        result = await session.execute(stmt)
        return result.scalar()