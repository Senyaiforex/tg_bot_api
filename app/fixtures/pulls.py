from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_pull(session: AsyncSession):
    """
    Функция для добавления категорий в базу данных
    """
    from models import Pull
    result = await session.execute(select(Pull).limit(1))
    liquid_current = result.scalar_one_or_none()
    if liquid_current:  # пулл уже задан
        return

    pull_start = Pull(farming=5_000_000,
                      task=5_000_000,
                      friends=5_000_000,
                      coins=5_000_000,
                      plan=5_000_000)
    session.add(pull_start)
    await session.commit()
