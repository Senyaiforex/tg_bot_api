from database import async_session

async def create_ranks(session: async_session):
    """
    Функция для добавления рангов в базу данных
    :param session:
    :return:
    """
    from models import Rank, RankEnum

    # Изначальные параметры
    initial_coins = 100_000
    initial_friends = 1
    initial_tasks = 10

    # Ранги
    ranks = ['stone', 'copper', 'silver', 'gold', 'platinum', 'diamond', 'sapphire', 'ruby', 'amethyst', 'morganite']

    for rank in range(1, 11):  # 10 рангов
        for level in range(1, 11):  # 10 уровней в каждом ранге
            if rank == 1 and level == 1:
                rank_entry = Rank(
                        rank=RankEnum(rank),
                        level=1,
                        required_coins=0,
                        required_friends=0,
                        required_tasks=0
                )
                session.add(rank_entry)
                continue
            else:
                rank_entry = Rank(
                        rank=RankEnum(rank),
                        level=(rank - 1) * 10 + level,
                        required_coins=initial_coins,
                        required_friends=initial_friends,
                        required_tasks=initial_tasks
                )
                if rank < 6:
                    initial_coins += 100_000
                elif rank == 6:
                    initial_coins += 500_000
                elif rank == 7:
                    initial_coins += 1_500_000
                elif rank == 8:
                    initial_coins += 2_500_000
                elif rank == 9:
                    initial_coins += 5_000_000
                elif rank == 10:
                    initial_coins += 10_000_000
                initial_friends += 1
                initial_tasks += 10
            session.add(rank_entry)

    await session.commit()
