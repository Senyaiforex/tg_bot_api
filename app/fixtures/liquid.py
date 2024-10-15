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

    liquid_start = LiquidPosts(free_posts=990, current_free=0,
                               coins_posts=4, current_coins=0,
                               money_posts=3, current_money=0,
                               token_posts=2, current_token=0,
                               stars_posts=1, current_stars=0)
    session.add(liquid_start)
    await session.commit()
