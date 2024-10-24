from sqlalchemy import Column, String, Integer, Date, ForeignKey, Boolean
from .users import users_tasks
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy_utils.types.choice import ChoiceType


class Task(Base):
    """
    Модель задач, которые может выполнять пользователь
    """
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories_tasks.id'))
    description = Column(String, comment='Описание')
    url = Column(String, comment='Ссылка на задачу', index=True)
    users = relationship("User", secondary=users_tasks, back_populates='tasks')
    date_limit = Column(Date, comment="Дата действия задания")
    active = Column(Boolean, default=True, comment="Активность")


class CategoryTask(Base):
    """
    Модель задач, которые может выполнять пользователь
    """
    TYPES = [
            ('task', 'Задания'),
            ('subscribe', 'Подписаться на канал'),
            ('watch', 'Просмотр видео'),
            ('games', 'Игры'),
            ('bonus', 'Бонусы')
    ]
    __tablename__ = 'categories_tasks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(ChoiceType(TYPES), comment='Название категории')
    tasks = relationship("Task", backref='category')