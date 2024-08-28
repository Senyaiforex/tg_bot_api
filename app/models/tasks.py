from sqlalchemy import Column, String, Integer
from .users import users_tasks
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy_utils.types.choice import ChoiceType
class Task(Base):
    """
    Модель задач, которые может выполнять пользователь
    """
    TYPES = [
            ('subscribe_channel', 'Подписаться на канал'),
            ('view_video', 'Просмотр видео'),
            ('like', 'Поставить лайк или добавить в избранное'),
            ('comment', 'Оставить комментарий')
    ]
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    type_task = Column(ChoiceType(TYPES))
    description = Column(String)
    users = relationship("User", secondary=users_tasks, back_populates='tasks')
