from datetime import datetime

from sqlalchemy import Column, Integer, BigInteger, Date
from database import Base


class CountSellers(Base):
    """
    Модель количества продавцов
    """
    __tablename__ = 'sellers'
    id = Column(Integer, primary_key=True)
    count = Column(Integer, comment='Количество продавцов', default=0)
    subscribes_count = Column(Integer, comment='Количество пользователей в группе', default=0)
    created_at = Column(Date, default=datetime.utcnow)