from email.policy import default
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    id_telegram: int = Field(
            ...,
            title='ID пользователя телеграм'
    )
    user_name: str = Field(
            ...,
            title='Никнейм пользователя'
    )
    count_token: str = Field(
            default=0,
            title='Количество токенов у пользователя'
    )
    count_pharmd: int = Field(
            default=65_000,
            title='Количество фарма у пользователя'
    )
    level: int = Field(
            default=0,
            title='Уровень'
    )
    count_invited_friends: int = Field(
            default=0,
            title='Количество приглашенных пользователей'
    )
    purchase_count: int = Field(
            default=0,
            title='Количество покупок'
    )
    sale_count: int = Field(
            default=0,
            title='Количество продаж'
    )
    registration_date: datetime = Field(
            title='Дата регистрации'
    )

    class Config:
        from_attributes = True


class ChangeToken(BaseModel):
    id_telegram: int
    amount: int
    add: bool


class ChangePharmd(BaseModel):
    id_telegram: int
    amount: int
    add: bool


class DeleteUser(BaseModel):
    id_telegram: int

class ChangeLevel(BaseModel):
    id_telegram: int
    amount: int
    add: bool

class ChangePurchase(BaseModel):
    id_telegram: int
    amount: int

class ChangeSale(BaseModel):
    id_telegram: int
    amount: int

class ChangeCountFriends(BaseModel):
    id_telegram: int
    amount: int
    add: bool