from datetime import datetime
from sqlalchemy import Column, String, Integer, Table, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base, async_session
from .posts import Post
friends = Table(
    'friends', Base.metadata,
    Column('friend1_id_telegram', ForeignKey('users.id_telegram'), primary_key=True),
    Column('friend2_id_telegram', ForeignKey('users.id_telegram'), primary_key=True),
)

users_tasks = Table(
    'users_tasks', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('task_id', ForeignKey('tasks.id'), primary_key=True),
)

class User(Base):
    """
    Модель пользователя телеграм
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    id_telegram = Column(Integer, index=True, unique=True)
    user_name = Column(String, index=True)
    count_coins = Column(Integer, default=0)
    count_pharmd = Column(Integer, default=65_000)
    level = Column(Integer, default=0)
    count_invited_friends = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    sale_count = Column(Integer, default=0)
    registration_date = Column(Date, default=datetime.utcnow)
    history_transactions = relationship("HistoryTransaction", backref='user')
    posts = relationship("Post", backref='user')
    active = Column(Boolean, default=1)
    spinners = Column(Integer, default=0, comment='Количество спиннеров для рулетки')
    tasks = relationship("Task", secondary=users_tasks, back_populates='users', lazy='joined')
    friends = relationship(
            'User',
            secondary=friends,
            primaryjoin=id_telegram == friends.c.friend1_id_telegram,
            secondaryjoin=id_telegram == friends.c.friend2_id_telegram,
            back_populates='friends',
            foreign_keys=[friends.c.friend1_id_telegram, friends.c.friend2_id_telegram]
    )

    async def update_count_coins(self, session: async_session, amount: int, description: str, new=False):
        if new:
            self.count_coins = 0
        self.count_coins += amount
        await session.commit()
        transaction = HistoryTransaction(
                user_id=self.id,
                change_amount=amount,
                description=description
        )
        session.add(transaction)
        await session.commit()


class HistoryTransaction(Base):
    """
    Модель истории транзакций пользователя
    """
    __tablename__ = 'history_transactions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    change_amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)