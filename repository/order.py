from sqlalchemy import select, update
from models import Order
from database import async_session


class OrderRepository:
    @classmethod
    async def create_order(cls, session: async_session, amount: int, user_id: int,
                           username: str, post_id: int | None, description: str) -> Order:
        """
        Метод для создания нового заказа
        для оплаты публикации поста
        :param session: Асинхронная сессия
        :param amount: Сумма
        :param user_id: Телеграм ID пользователя
        :param username: Никнейм пользователя
        :param post_id: ID поста для публикации
        :return: инстанс Заказа
        :rtype: Order
        """
        new_order = Order(amount=amount, user_telegram=user_id,
                          post_id=post_id, user_name=username)
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        return new_order

    @classmethod
    async def update_order(cls, session: async_session, order_id: int, **kwargs) -> None:
        """
        Метод, для обновления данных заказа
        :param session: Асинхронная сессия
        :param order_id: ID заказа в БД
        :param kwargs: Данные для обновления
        :return: None
        """
        stmt = (
                update(Order).
                where(Order.id == order_id).
                values(kwargs)
        )
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_order(cls, session: async_session, order_id: int) -> Order:
        """
        Метод для получения заказа из БД по его ID
        :param session: Асинхронная сессия
        :param order_id:
        :return:
        """
        order_query = await session.execute(
                select(Order).
                where(Order.id == order_id)
        )
        result = order_query.scalars().first()
        return result
