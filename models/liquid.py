from sqlalchemy import Column, Integer, Boolean, String
from database import Base


class LiquidPosts(Base):
    """
    Модель для пула ликвидности размещения постов
    """
    __tablename__ = 'liquid'
    id = Column(Integer, primary_key=True, index=True)
    all_posts = Column(Integer, default=0)
    free_posts = Column(Integer, default=0)
    paid_posts = Column(Integer, default=0)
