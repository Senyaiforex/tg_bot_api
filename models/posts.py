from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, Date, BigInteger
from sqlalchemy_utils import ChoiceType

from database import Base


class Post(Base):
    """
    Модель объявления в группе/канале,
    которое может быть опубликован пользователем
    """
    TYPES = [
            ('free', 'Бесплатно'),
            ('coins', 'За монеты'),
            ('token', 'За токены'),
            ('money', 'За рубли'),
            ('stars', 'За звёзды')
    ]
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, comment='Название поста')
    method = Column(ChoiceType(TYPES), comment='Тип публикации')
    photo = Column(String, comment='Путь к фотографии поста')
    price = Column(Integer, comment='Цена на товар')
    discounted_price = Column(Integer, comment='Цена со скидкой')
    discount = Column(Integer, comment='Скидка')
    url_message = Column(String, comment='Ссылка на сообщение с постом в группе', nullable=True, index=True)
    url_message_main = Column(String, comment='Ссылка на сообщение с постом в основной группе', nullable=True)
    url_message_free = Column(String, comment='Ссылка на сообщение в бесплатной группе', nullable=True)
    active = Column(Boolean, default=False)
    marketplace = Column(String, comment='Маркетплейс', nullable=True)
    account_url = Column(String, comment='Ссылка на аккаунт')
    user_telegram = Column(BigInteger, ForeignKey('users.id_telegram'))
    channel_id = Column(String)
    date_public = Column(Date, nullable=True)
    date_expired = Column(Date, nullable=True)