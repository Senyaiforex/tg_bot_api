from pydantic import BaseModel, Field


class Tasks(BaseModel):
    id: int = Field(default=..., description='ID задачи')


class Task(BaseModel):
    id: int = Field(default=..., description='ID задачи')
    description: str = Field(default=..., description='Описание задачи')
