from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, friends


async def get_user_bot(telegram_id: int, session: AsyncSession):
    """
    Функция дял получения пользователя из базы данных по id_telegram
    :param telegram_id:
    :param session:
    :return:
    """
    result = await session.execute(select(User).where(User.id_telegram == telegram_id))
    user = result.scalars().one_or_none()
    return user


async def handle_invitation(inviter_id: int, user_id: int, username: str, session: AsyncSession) -> None:
    """
     Функция обработки приглашения пользователя
    :param inviter_id: id пользователя, который пригласил.
    :param user_id: id пользователя, который получил приглашение.
    :return:
    """

    inviter = await session.execute(select(User).where(User.id_telegram == inviter_id))
    inviter = inviter.scalars().first()
    query = await session.execute(select(User).filter(User.id_telegram == user_id))
    user = query.scalars().one_or_none()
    if user:
        return
    await inviter.update_count_coins(session, 5000, f"Приглашение друга")
    inviter.count_invited_friends += 1
    new_user = User(id_telegram=user_id,
                    user_name=username)
    await new_user.update_count_coins(session, 5000, f"Бонус за регистрацию", new=True)
    session.add(new_user)
    await session.execute(friends.insert().values(
            friend1_id_telegram=inviter_id,
            friend2_id_telegram=user_id
    ))
    await session.commit()
