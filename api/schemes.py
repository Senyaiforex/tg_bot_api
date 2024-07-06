from typing import Optional

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
