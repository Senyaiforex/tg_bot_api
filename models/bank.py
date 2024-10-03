from sqlalchemy import Column, Integer, BigInteger
from database import Base


class Bank(Base):
    """
    Модель общего количества монет, которые списываются с пользователей
    """
    __tablename__ = 'bank'
    id = Column(Integer, primary_key=True)
    coins = Column(BigInteger, index=True, default=0)