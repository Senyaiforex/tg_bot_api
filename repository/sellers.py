from sqlalchemy import select, update
from models import CountSellers
from database import async_session


class SellerRepository:
    @classmethod
    async def get_count_sellers(cls, session: async_session) -> int:
        """
        Метод для получения количества продавцов
        :param session: Асинхронная сессия
        :rtype: int
        """
        stmt = select(CountSellers.count).where(CountSellers.id == 1)
        result = await session.execute(stmt)
        count = result.scalar_one_or_none()
        return count if count else 0

    @classmethod
    async def get_count_users(cls, session: async_session) -> int:
        """
        Метод для получения количества подписчиков в группе
        :param session: Асинхронная сессия
        :rtype: int
        """
        stmt = select(CountSellers.subscribes_count).where(CountSellers.id == 1)
        result = await session.execute(stmt)
        count = result.scalar_one_or_none()
        return count if count else 0

    @classmethod
    async def seller_add(cls, session: async_session) -> None:
        """
        Метод для увеличения количества продавцов в БД
        :param session: Асинхронная сессия
        :return: None
        """
        stmt = (
                update(CountSellers).
                where(CountSellers.id == 1).
                values(count=CountSellers.count + 1)
        )

        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def sellers_clear(cls, subscribes_count: int, session: async_session) -> None:
        """
        Метод для очистки количества продавцов в БД
        :param session: Асинхронная сессия
        :return: None
        """
        stmt = (
                update(CountSellers).
                where(CountSellers.id == 1).
                values(count=0,
                       subscribes_count=subscribes_count)
        )

        await session.execute(stmt)
        await session.commit()
