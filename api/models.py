from sqlalchemy import Column, String, Integer

from api.database import Base


class User(Base):
    """
    Модель пользователя телеграм
    """
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index=True)
    id_telegram = Column(Integer, index=True, unique=True)
    user_name = Column(String, index=True)
    count_tokens = Column(Integer, index=True, default=0)
    count_pharmd = Column(Integer, index=True, default=65_000)