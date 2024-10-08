import random
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def create_random_users(session: AsyncSession):
    users = []
    today = datetime.today().date()
    from models import User
    result = await session.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user:  # посты уже есть в базе
        return
    for _ in range(20):
        # Генерация случайных данных для пользователя
        user_name = f"test_{random.randint(1000, 9999)}"
        id_telegram = random.randint(1000000, 9999999)
        total_coins = random.choice(range(10000, 40001, 1000))
        count_coins = random.choice(range(10000, 50001, 1000))
        registration_date = today - timedelta(days=random.randint(0, 30))
        user = User(
            user_name=user_name,
            id_telegram=id_telegram,
            total_coins=total_coins,
            count_coins=count_coins,
            registration_date=registration_date
        )
        users.append(user)
    session.add_all(users)
    await session.commit()

async def create_admins(session: AsyncSession):
    from models import User
    result = await session.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user:  # посты уже есть в базе
        return
    user_name = "NFT_Bro"
    user_id = 5321413149
    user_1 = User(
            user_name=user_name,
            id_telegram=user_id,
            count_coins = 1000000,
            superuser=True,
            registration_date=datetime.today().date()
    )
    user_2 = User(
            user_name="senyaiforex",
            id_telegram=718586333,
            count_coins = 10000000,
            superuser=True,
    )
    session.add_all([user_1, user_2])
    await session.commit()