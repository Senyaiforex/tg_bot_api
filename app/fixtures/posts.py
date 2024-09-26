import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def create_random_posts(session: AsyncSession):
    marketplaces = ['OZON', 'WILDBERRIES', 'Нет']
    file_paths = [f'/path/to/file_{i}.jpg' for i in range(1, 201)]
    TYPES = [
            ('free', 'Бесплатно'),
            ('coins', 'За монеты'),
            ('token', 'За токены'),
            ('money', 'За рубли'),
            ('stars', 'За звёзды')
    ]
    from models import User, Post
    result = await session.execute(select(Post).limit(1))
    post = result.scalar_one_or_none()
    if post:  # посты уже есть в базе
        return
    today = datetime.today().date()
    start_date = today - timedelta(days=40)
    # Получение всех пользователей из базы данных
    result = await session.execute(select(User))
    users = result.scalars().all()

    posts = []

    for _ in range(200):
        user = random.choice(users)
        name = f"Post_{random.randint(1000, 9999)}"
        method = method = random.choice(TYPES)[0]
        photo = random.choice(file_paths)
        price = random.randint(1, 100)
        discount = random.randint(1, 100)
        discounted_price = price - (price * discount // 100)
        date_public = start_date + timedelta(days=random.randint(0, 40))
        marketplace = random.choice(marketplaces)

        post = Post(
                name=name,
                method=method,
                photo=photo,
                price=price,
                discounted_price=discounted_price,
                discount=discount,
                url_message=None,
                url_message_main=None,
                active=random.choice([True, False]),
                marketplace=marketplace,
                account_url=user.user_name,
                user_telegram=user.id_telegram,
                channel_id=f"channel_{random.randint(1, 1000)}",
                date_public=date_public,
                date_expired=date_public + timedelta(days=7)
        )
        posts.append(post)
    session.add_all(posts)
    await session.commit()
