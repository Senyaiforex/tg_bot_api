from sqlalchemy import Column, String, Integer, Table, func, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

users_tasks = Table('users_tasks', Base.metadata,
                    Column('user_id', ForeignKey('users.id'), primary_key=True),
                    Column('task_id', ForeignKey('tasks.id'), primary_key=True)
                    )
friends = Table(
        'friends', Base.metadata,
        Column('friend1_id', ForeignKey('users.id'), primary_key=True),
        Column('friend2_id', ForeignKey('users.id'), primary_key=True)
)


class User(Base):
    """
    Модель пользователя телеграм
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    id_telegram = Column(Integer, index=True, unique=True)
    user_name = Column(String, index=True)
    count_tokens = Column(Integer, index=True, default=0)
    count_pharmd = Column(Integer, index=True, default=65_000)
    level = Column(Integer, default=0)
    count_invited_friends = Column(Integer, index=True, default=0)
    purchase_count = Column(Integer, index=True, default=0)  # Количество покупок
    sale_count = Column(Integer, index=True, default=0)      # Количество продаж
    registration_date = Column(DateTime, default=func.now()) # Дата регистрации

    tasks = relationship("Task", secondary="users_tasks", back_populates='tasks')
    friends = relationship('User', secondary='friends', back_populates='friends')

class Task(Base):
    """
    Модель задач, которые может выполнять пользователь
    """
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    users = relationship("User", secondary="users_tasks", back_populates='users')
