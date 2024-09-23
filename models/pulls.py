from sqlalchemy import Column, Integer
from database import Base


class Pull(Base):
    """
    Модель пула, который задаёт администратор
    """
    __tablename__ = 'pulls'
    id = Column(Integer, primary_key=True, index=True)
    farming = Column(Integer, comment='Пулл для фарминга')
    task = Column(Integer, comment='Пулл для заданий')
    friends = Column(Integer, comment='Пулл для друзей')
    plan = Column(Integer, comment='Пулл для краудсорсинга')
    coins = Column(Integer, comment='Пулл для монет')
    __table_args__ = {'extend_existing': True}
    current_farming = Column(Integer, comment='Текущий фарминг', default=0)
    current_task = Column(Integer, comment='Текущее количество пулла по заданиям', default=0)
    current_friends = Column(Integer, comment='Текущее количество пулла по друзьям', default=0)
    current_coins = Column(Integer, comment='Текущее количество пулла по монетам', default=0)
    current_plan = Column(Integer, comment='Текущее количество пулла по краудсорсингу', default=0)