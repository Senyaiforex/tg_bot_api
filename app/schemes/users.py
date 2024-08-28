from email.policy import default
from typing import Optional, List
from datetime import date, datetime
from .tasks import Tasks
from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    id_telegram: int = Field(
            ...,
            description='ID пользователя телеграм',
            gt=0
    )
    user_name: str = Field(
            ...,
            description='Никнейм пользователя'
    )
    count_coins: int = Field(
            default=0,
            description='Количество токенов у пользователя'
    )
    count_pharmd: int = Field(
            default=65_000,
            description='Количество фарма у пользователя'
    )
    level: int = Field(
            default=0,
            description='Уровень'
    )
    count_invited_friends: int = Field(
            default=0,
            description='Количество приглашенных пользователей'
    )
    purchase_count: int = Field(
            default=0,
            description='Количество покупок'
    )
    sale_count: int = Field(
            default=0,
            description='Количество продаж'
    )
    registration_date: date = Field(
            description='Дата регистрации',
    )


class UserIn(BaseUser):
    ...


class Friend(BaseModel):
    user_name: str = Field(default=..., description='Никнейм друга')
    count_coins: int = Field(default=..., description='Количество монет друга')
    level: int = Field(default=..., description='Уровень друга')


class UserOut(BaseUser):
    friends: Optional[List[Friend]] = Field(default=[], description='Друзья')
    tasks: Optional[List[Tasks]] = Field(default=[], description='Задачи')

    class Config:
        from_orm = True
        related_fields = {'friends': {'exclude': ['id_telegram', 'count_pharmd',
                                                  'registration_date', 'purchase_count',
                                                  'sale_count', 'count_invited_friends', ]},
                          'tasks': {'exclude': ['description', 'users']}}


class DeleteUser(BaseModel):
    id_telegram: int


class HistoryTransactionOut(BaseModel):
    id: int = Field(..., description='ID транзакции')
    change_amount: int = Field(..., description='Изменение количества')
    description: str = Field(..., description='Описание транзакции')
    transaction_date: datetime | str = Field(..., description='Дата транзакции')

    class Config:
        from_attributes = True


class UserTopOut(BaseModel):
    id_telegram: int = Field(..., description='ID пользователя')
    user_name: str = Field(..., description='Никнейм пользователя')
    count_coins: int = Field(..., description='Количество токенов')


class TopUsers(BaseModel):
    top_users: List[UserTopOut] = []


class HistoryTransactionList(BaseModel):
    transactions: List[HistoryTransactionOut] = []
