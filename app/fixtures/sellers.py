from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

async def create_sellers(session: AsyncSession):
    """
    Функция для добавления записи продавцов
    """
    from models import CountSellers
    result = await session.execute(select(CountSellers).limit(1))
    sellers = result.scalar_one_or_none()
    if sellers:  # ликвидность уже задана
        return

    seller_start = CountSellers(count=0, created_at=datetime.datetime.today().date())
    session.add(seller_start)
    await session.commit()
