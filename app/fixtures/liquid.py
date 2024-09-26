from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_liquid(session: AsyncSession):
    """
    Функция для добавления категорий в базу данных
    """
    from models import LiquidPosts
    result = await session.execute(select(LiquidPosts).limit(1))
    liquid_current = result.scalar_one_or_none()
    if liquid_current:  # ликвидность уже задана
        return

    liquid_start = LiquidPosts(free_posts=990,
                               coins_posts=5,
                               money_posts=3,
                               token_posts=2)
    session.add(liquid_start)
    await session.commit()
