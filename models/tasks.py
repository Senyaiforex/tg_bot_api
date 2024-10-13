from sqlalchemy import Column, String, Integer, Date, ForeignKey
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


class CategoryTask(Base):
    """
    Модель задач, которые может выполнять пользователь
    """
    TYPES = [
            ('subscribe', 'Подписаться на канал'),
            ('games', 'Игры'),
            ('watch', 'Просмотр видео'),
            ('like', 'Поставить лайк или добавить в избранное'),
            ('comment', 'Оставить комментарий'),
            ('save', 'Добавить в избранное'),
            ('bonus', 'Бонусы')
    ]
    __tablename__ = 'categories_tasks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(ChoiceType(TYPES), comment='Название категории')
    tasks = relationship("Task", backref='category')