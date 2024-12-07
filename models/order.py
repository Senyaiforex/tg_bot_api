from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, String, BigInteger, Date
from database import Base


class Order(Base):
    """
    Модель заказа для покупки размещения поста
    """
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, default=0)
    user_telegram = Column(BigInteger, nullable=True)
    user_name = Column(String, nullable=True)
    post_id = Column(Integer, nullable=True)
    paid = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    date_created = Column(Date, default=datetime.utcnow)