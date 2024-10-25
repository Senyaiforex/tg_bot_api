from datetime import datetime
from functools import wraps

from sqlalchemy import Column, String, Integer, Table, ForeignKey, Date, DateTime, Boolean, select, BigInteger
from sqlalchemy.orm import relationship
from database import Base, async_session
from .posts import Post

friends = Table(
        'friends', Base.metadata,
        Column('friend1_id_telegram', ForeignKey('users.id_telegram'),
               primary_key=True),
        Column('friend2_id_telegram', ForeignKey('users.id_telegram'),
               primary_key=True),
)

users_tasks = Table(
        'users_tasks', Base.metadata,
        Column('user_id', ForeignKey('users.id', ondelete='CASCADE'),
               primary_key=True),
        Column('task_id', ForeignKey('tasks.id', ondelete='CASCADE'),
               primary_key=True),
)


def rank_updater(func):
    """
    Декоратор для обновления ранга при каких-либо изменениях в модели User
    :param func:
    :return:
    """

    @wraps(func)
    async def wrapper(self, session: async_session, *args, **kwargs):
        await func(self, session, *args, **kwargs)
        try:
            if self.rank_id != 100:
                from .rank import Rank
                result = await session.execute(select(Rank)
                                               .where(Rank.id == self.rank_id + 1))
                rank_next = result.scalars().first()
                if (self.count_invited_friends and
                        all((self.count_invited_friends >= rank_next.required_friends,
                             self.total_coins >= rank_next.required_coins,
                             self.count_tasks >= rank_next.required_tasks))):
                    self.spinners += 3
                    self.rank_id = rank_next.id
        except TypeError as ex:
            pass
        await session.commit()

    return wrapper


class User(Base):
    """
    Модель пользователя телеграм
    """
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, index=True)
    id_telegram = Column(BigInteger, index=True, unique=True)
    user_name = Column(String, index=True)
    count_coins = Column(Integer, default=0)
    count_pharmd = Column(Integer, default=2_000)
    total_coins = Column(Integer, default=0)
    count_invited_friends = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    sale_count = Column(Integer, default=0)
    registration_date = Column(Date, default=datetime.utcnow)
    history_transactions = relationship("HistoryTransaction",
                                        backref='user')
    posts = relationship("Post", backref='user')
    active = Column(Boolean, default=1)
    admin = Column(Boolean, default=0)
    superuser = Column(Boolean, default=0)
    spinners = Column(Integer, default=0, comment='Количество спиннеров для рулетки')
    tasks = relationship("Task", secondary=users_tasks,
                         back_populates='users')
    count_tasks = Column(Integer, default=0, comment='Количество выполненных задач')
    count_free_posts = Column(Integer, default=0, nullable=False,
                              comment='Количество бесплатных размещённых постов')
    rank_id = Column(Integer, ForeignKey('ranks.id'), default=1)
    friends = relationship(
            'User',
            secondary=friends,
            primaryjoin=id_telegram == friends.c.friend1_id_telegram,
            secondaryjoin=id_telegram == friends.c.friend2_id_telegram,
            back_populates='friends',
            foreign_keys=[friends.c.friend1_id_telegram,
                          friends.c.friend2_id_telegram]
    )
    search_posts = relationship('SearchPost',
                                backref='user'
                                )

    @rank_updater
    async def update_count_coins(self, session: async_session, amount: int,
                                 description: str, new=False, add=True):
        if new:
            self.count_coins = 0
            self.total_coins = 0
        self.count_coins += amount
        self.total_coins += amount
        transaction = HistoryTransaction(
                user_id=self.id,
                change_amount=amount,
                description=description,
                add=add
        )
        session.add(transaction)

    @rank_updater
    async def set_friends(self, session: async_session, amount: int):
        if not self.count_invited_friends:
            self.count_invited_friends = 0
        self.count_invited_friends += amount

    @rank_updater
    async def set_tasks(self, session: async_session, amount: int):
        if not self.count_tasks:
            self.count_tasks = 0
        self.count_tasks += amount


class HistoryTransaction(Base):
    """
    Модель истории транзакций пользователя
    """
    __tablename__ = 'history_transactions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    change_amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    add = Column(Boolean, nullable=True, default=True)
    transaction_date = Column(DateTime,
                              default=datetime.utcnow,
                              nullable=False)


class SearchPost(Base):
    """
    Модель товара в листе ожидания
    """
    __tablename__ = 'search_post'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,
                  comment='Название товара для поиска',
                  index=True,
                  nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
