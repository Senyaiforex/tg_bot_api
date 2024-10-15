from sqlalchemy import Column, Integer, Boolean, String
from database import Base


class LiquidPosts(Base):
    """
    Модель для пула ликвидности размещения постов
    """
    __tablename__ = 'liquid'
    id = Column(Integer, primary_key=True, index=True)
    free_posts = Column(Integer, default=0)
    coins_posts = Column(Integer, default=0)
    money_posts = Column(Integer, default=0)
    token_posts = Column(Integer, default=0)
    stars_posts = Column(Integer, default=0)
    current_free = Column(Integer, default=0)
    current_coins = Column(Integer, default=0)
    current_money = Column(Integer, default=0)
    current_stars = Column(Integer, default=0)
    current_token = Column(Integer, default=0)
