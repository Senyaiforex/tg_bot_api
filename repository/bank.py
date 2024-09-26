from sqlalchemy import select, update
from models import Bank
from database import async_session


class BankRepository:
    @classmethod
    async def get_bank_coins(cls, session: async_session) -> int:
        """
        Метод для получения количества монет в общем банке приложения
        :param session: Асинхронная сессия
        :return: количество монет
        :rtype: int
        """
        bank_id = 1
        stmt = select(Bank.coins).where(Bank.id == bank_id)
        result = await session.execute(stmt)
        coins = result.scalar_one_or_none()
        return coins

    @classmethod
    async def bank_update(cls, session: async_session, amount: int) -> None:
        """
        Метод для обновления данных в общем банке монет приложения
        :param session: Асинхронная сессия
        :param amount: Количество
        :return: None
        """
        bank_id = 1
        stmt = (
                update(Bank).
                where(Bank.id == bank_id).
                values(coins=Bank.coins + amount)
        )

        await session.execute(stmt)
        await session.commit()
