from typing import List

from pydantic import BaseModel, Field


class PostsByType(BaseModel):
    name: str = Field(default=..., description='Название типа')
    price: int = Field(default=..., description='Стоимость размещения')
    data: List[int] = Field(default=..., description='Данные по ликвидности')
    current: int = Field(default=..., description='Количество публикаций')
    need: int = Field(default=..., description='Требуемое количество публикаций')

dict_t = [{'name': 'ПОсты за рубли',
           "price": '1450',
           "data": [50, 50]},
          {'name': 'Посты за монеты',
           "price": '10000',
           "data": [60, 40]},
          {'name': 'Посты за токены',
           "price": '20000',
           "data": [70, 30]}]
