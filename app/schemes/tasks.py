from pydantic import BaseModel, Field, field_validator
from sqlalchemy_utils.types import Choice


class TaskOut(BaseModel):
    id: int = Field(default=..., description='ID задачи')
    description: str = Field(default=..., description='Описание задачи')
    url: str = Field(default=..., description='Ссылка')
    type_task: str = Field(default=..., description='Тип задачи')

    @field_validator('type_task', mode='before')
    def format_transaction_date(cls, v):
        if isinstance(v, Choice):
            return v.code

    class Config:
        from_attributes = True


class TaskByUser(BaseModel):
    id: int = Field(default=..., description='ID задачи')

    class Config:
        from_attributes = True
