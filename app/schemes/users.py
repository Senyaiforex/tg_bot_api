from email.policy import default
from typing import Optional, List
from datetime import date, datetime
from .tasks import TaskByUser, TaskOut
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Enum


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
    registration_date: date | str = Field(
            description='Дата регистрации',
    )
    active: bool = Field(
            description='Активность пользователя'
    )


class UserIn(BaseUser):
    ...


class Rank(BaseModel):
    id: int = Field(..., description='ID ранга')
    rank: str = Field(default=..., description='Название ранга')
    level: int = Field(default=..., description='Уровень')

    @field_validator('rank', mode='before')
    def format_transaction_date(cls, v):
        return v.name

    class Config:
        from_attributes = True


class UserOut(BaseUser):
    active: bool = Field(default=True, description='Активность')
    spinners: int = Field(
            default=0,
            description='Количество спиннеров для рулетки'
    )
    count_tasks: int = Field(default=0, description='Количество выполненных задач')
    rank: Rank
    next_level_coins: int = Field(
            description='Количество монет, необходимых для следующего уровня'
    )
    next_level_friends: int = Field(
            description='Количество друзей, необходимых для следующего уровня'
    )
    next_level_tasks: int = Field(
            description='Количество задач, необходимых для следующего уровня'
    )

    class Config:
        from_attributes = True

    @field_validator('registration_date', mode='before')
    def format_transaction_date(cls, v):
        if isinstance(v, date):
            return v.strftime('%d-%m-%Y')
        return v


class Friend(BaseModel):
    user_name: str = Field(default=..., description='Никнейм друга')
    count_coins: int = Field(default=..., description='Количество монет друга')
    level: int = Field(default=..., description='Уровень друга')


class DeleteUser(BaseModel):
    id_telegram: int


class HistoryTransactionOut(BaseModel):
    id: int = Field(..., description='ID транзакции')
    change_amount: int = Field(..., description='Изменение количества')
    description: str = Field(..., description='Описание транзакции')
    transaction_date: datetime | str = Field(..., description='Дата транзакции')

    @field_validator('transaction_date', mode='before')
    def format_transaction_date(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%d-%m-%Y %H:%M')
        elif isinstance(v, str):
            try:
                parsed_date = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                return parsed_date.strftime('%d-%m-%Y %H:%M')
            except ValueError:
                pass
        return v

    class Config:
        from_attributes = True


class UserTopOut(BaseModel):
    id_telegram: int = Field(..., description='ID пользователя')
    user_name: str = Field(..., description='Никнейм пользователя')
    count_coins: int = Field(..., description='Количество токенов')
