from sqlalchemy import Column, Integer, BigInteger
from database import Base


class Pull(Base):
    """
    Модель пула, который задаёт администратор
    """
    __tablename__ = 'pulls'
    id = Column(Integer, primary_key=True, index=True)
    farming = Column(BigInteger, comment='Пулл для фарминга')
    tasks = Column(BigInteger, comment='Пулл для заданий')
    friends = Column(BigInteger, comment='Пулл для друзей')
    plan = Column(BigInteger, comment='Пулл для краудсорсинга')
    coins = Column(BigInteger, comment='Пулл для монет')
    __table_args__ = {'extend_existing': True}
    current_farming = Column(BigInteger, comment='Текущий фарминг', default=0)
    current_tasks = Column(BigInteger, comment='Текущее количество пулла по заданиям', default=0)
    current_friends = Column(BigInteger, comment='Текущее количество пулла по друзьям', default=0)
    current_coins = Column(BigInteger, comment='Текущее количество пулла по монетам', default=0)
    current_plan = Column(BigInteger, comment='Текущее количество пулла по краудсорсингу', default=0)