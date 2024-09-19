from sqlalchemy import Column, Integer
from database import Base


class Bank(Base):
    """
    Модель общего количества монет, которые списываются с пользователей
    """
    __tablename__ = 'bank'
    id = Column(Integer, primary_key=True, index=True)
    coins = Column(Integer, index=True, default=0)