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
