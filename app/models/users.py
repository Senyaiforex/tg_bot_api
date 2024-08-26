from datetime import datetime
from sqlalchemy import Column, String, Integer, Table, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from database import Base, async_session

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
    count_coins = Column(Integer, index=True, default=0)
    count_pharmd = Column(Integer, index=True, default=65_000)
    level = Column(Integer, default=0)
    count_invited_friends = Column(Integer, index=True, default=0)
    purchase_count = Column(Integer, index=True, default=0)  # Количество покупок
    sale_count = Column(Integer, index=True, default=0)  # Количество продаж
    registration_date = Column(Date, default=datetime.utcnow)  # Дата регистрации
    history_transactions = relationship("HistoryTransaction", backref='user')  # История
    tasks = relationship("Task", secondary=users_tasks, back_populates='users', lazy='joined')
    friends = relationship(
            'User',
            secondary=friends,
            primaryjoin=id_telegram == friends.c.friend1_id_telegram,
            secondaryjoin=id_telegram == friends.c.friend2_id_telegram,
            back_populates='friends',
            foreign_keys=[friends.c.friend1_id_telegram, friends.c.friend2_id_telegram]
    )

    async def update_count_coins(self, session: async_session, amount: int, description: str):
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
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    change_amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
