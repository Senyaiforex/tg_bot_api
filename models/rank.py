from sqlalchemy import Column, Integer, Enum, BigInteger
from sqlalchemy.orm import relationship
from .users import User
from database import Base
import enum


class RankEnum(enum.Enum):
    stone = 1
    copper = 2
    silver = 3
    gold = 4
    platinum = 5
    diamond = 6
    sapphire = 7
    ruby = 8
    amethyst = 9
    morganite = 10


class Rank(Base):
    """
    Модель для хранения требований к уровням в рангах.
    """
    __tablename__ = 'ranks'

    id = Column(Integer, primary_key=True, index=True)
    rank = Column(Enum(RankEnum), default=RankEnum.stone, comment="Ранг пользователя")
    level = Column(Integer, nullable=False, comment="Уровень в ранге")
    required_coins = Column(Integer, nullable=False, comment="Требуемое количество монет")
    required_friends = Column(Integer, nullable=False, comment="Требуемое количество друзей")
    required_tasks = Column(Integer, nullable=False, comment="Требуемое количество выполненных задач")
    users = relationship("User",
                         backref='rank')
