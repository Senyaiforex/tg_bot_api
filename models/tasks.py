from pydantic import field_validator
from sqlalchemy import Column, String, Integer, Date
from .users import users_tasks
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy_utils.types.choice import ChoiceType


class Task(Base):
    """
    Модель задач, которые может выполнять пользователь
    """
    TYPES = [
            ('subscribe', 'Подписаться на канал'),
            ('watch', 'Просмотр видео'),
            ('like', 'Поставить лайк или добавить в избранное'),
            ('comment', 'Оставить комментарий'),
            ('save', 'Добавить в избранное')
    ]
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    type_task = Column(ChoiceType(TYPES), comment='Тип задачи')
    description = Column(String, comment='Описание')
    url = Column(String, comment='Ссылка на задачу', index=True)
    users = relationship("User", secondary=users_tasks, back_populates='tasks')
    date_limit = Column(Date, comment="Дата действия задания")