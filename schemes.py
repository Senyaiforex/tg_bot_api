from email.policy import default
from typing import Optional, List
from datetime import date

from pydantic import BaseModel, Field, HttpUrl

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
    count_token: str = Field(
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
    # tasks: Optional[List[int]] = Field(default=None, description='Задачи пользователя')
    # friends: Optional[List[int]] = Field(default=None, description='Друзья пользователя')
class UserIn(BaseUser):
    ...

class UserOut(BaseUser):
    class Config:
        from_orm = True




class Task(BaseModel):
    id: int = Field(default=..., description='ID задачи')
    description: str = Field(default=..., description='Описание задачи')

class Friends(BaseModel):
    friend1_id: int = Field(default=..., description='ID первого друга')
    friend2_id: int = Field(default=..., description='ID второго друга')

class ChangeToken(BaseModel):
    amount: int
    add: bool


class ChangePharmd(BaseModel):
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
