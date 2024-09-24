from sqlalchemy.ext.asyncio import AsyncSession


async def create_categories(session: AsyncSession):
    """
    Функция для добавления категорий в базу данных
    """
    from models import CategoryTask
    categories = [
            'subscribe', 'games', 'watch', 'like', 'comment', 'save', 'bonus'
    ]

    for category in categories:
        category_entry = CategoryTask(name=category)
        session.add(category_entry)

    await session.commit()
