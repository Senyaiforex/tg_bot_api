from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_bank(session: AsyncSession):
    """
    Функция для добавления категорий в базу данных
    """
    from models import Bank
    result = await session.execute(select(Bank).limit(1))
    bank = result.scalar_one_or_none()
    if bank:  # банк уже есть
        return

    bank = Bank(coins=0)
    session.add(bank)
    await session.commit()