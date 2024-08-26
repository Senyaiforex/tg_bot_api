from sqlalchemy import Column, String, Integer
from .users import users_tasks
from sqlalchemy.orm import relationship
from database import Base


class Task(Base):
    """
    Модель задач, которые может выполнять пользователь
    """
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    users = relationship("User", secondary=users_tasks, back_populates='tasks')
