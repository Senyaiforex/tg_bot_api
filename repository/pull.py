from sqlalchemy import select, update
from models import Pull
from database import async_session


class PullRepository:
    @classmethod
    async def get_pull(cls, session: async_session) -> Pull:
        """
        Функция для получения пула
        :param session: Асинхронная сессия
        :return: Pull
        """
        pull = await session.execute(
                select(Pull)
        )
        return pull.scalars().first()

    @classmethod
    async def update_pull(cls, session: async_session, amount: int, type_pull: str) -> None:
        """
        Метод для обновления пула
        :param session: Асинхронная сессия
        :param amount: Количество
        :param type_pull: Тип пула (current_task, current_farming, current_friends, current_coins, current_plan)
        :return:
        """
        pull_query = await session.execute(
                select(Pull)
        )
        pull = pull_query.scalars().first()
        setattr(pull, type_pull, pull.__getattribute__(type_pull) + amount)
        await session.commit()

    @classmethod
    async def set_pull_size(cls, dict_pull_sizes: dict, session: async_session) -> None:
        """
        Функция для изменения пулла
        :param dict_pull_sizes: словарь со значениями параметров
        :param session: Асинхронная сессия
        :return: None
        """
        pull_query = await session.execute(select(Pull))
        pull = pull_query.scalars().first()
        for key, value in dict_pull_sizes.items():
            setattr(pull, key, value)

        await session.commit()
