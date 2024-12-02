from database import async_session
from sqlalchemy import select
from models import Rank


class RankRepository:
    @classmethod
    async def get_next_rank(cls, rank_id: int, session: async_session) -> Rank:
        """
        Метод для получения следующего ранга, у которого id > чем rank_id на 1
        :param rank_id:
        :param session:
        :return:
        """
        result = await session.execute(
                select(Rank)
                .where(Rank.id == rank_id + 1)
        )
        rank = result.scalars().first()
        return rank
    @classmethod
    async def get_all_ranks(cls, session: async_session) -> list[Rank]:
        """
        Метод для получения всех рангов из базы данных с их уровнями
        :param session: Асинхронная сессия
        :return: список рангов
        :rtype: list[Rank]
        """
        list_levels_new_rank = [2, 11, 21, 31, 41, 51, 61, 71, 81, 91] # уровни, на которых достигается новый ранг
        result = await session.execute(
                select(Rank)
                .where(Rank.id.in_(list_levels_new_rank))
        )
        ranks = result.scalars().all()
        return ranks