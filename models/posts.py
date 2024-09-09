from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float
from database import Base


class Post(Base):
    __tablename__ = 'posts'
    marketplace = [
            ('WB', 'wildberries'),
            ('OZON', 'ozon'),
    ]
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, comment='Название поста')
    photo = Column(String, comment='Путь к фотографии поста')
    price = Column(Float, comment='Цена на товар')
    discounted_price = Column(Float, comment='Цена со скидкой')
    discount = Column(Float, comment='Скидка')
    user = Column(Integer, ForeignKey('users.id_telegram'))
    active = Column(Boolean)