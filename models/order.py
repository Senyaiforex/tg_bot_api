from sqlalchemy import Column, Integer, Boolean, String
from database import Base


class Order(Base):
    """
    Модель заказа для покупки размещения поста
    """
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, default=0)
    user_telegram = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False)
    post_id = Column(Integer, nullable=False)
    paid = Column(Boolean, default=False)