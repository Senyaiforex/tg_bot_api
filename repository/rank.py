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
        next_id = rank_id + 1
        result = await session.execute(
                select(Rank)
                .where(Rank.id == next_id)
        )
        rank = result.scalars().first()
        return rank
