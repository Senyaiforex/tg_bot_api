from sqlalchemy import Column, Integer
from database import Base


class Pull(Base):
    """
    Модель пула, который задаёт администратор
    """
    __tablename__ = 'pulls'
    id = Column(Integer, primary_key=True, index=True)
    pull_size = Column(Integer)
    __table_args__ = {'extend_existing': True}
