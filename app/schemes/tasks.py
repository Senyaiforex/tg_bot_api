from pydantic import BaseModel, Field, field_validator, root_validator, model_validator
from sqlalchemy_utils.types import Choice


class TaskOut(BaseModel):
    id: int = Field(default=..., description='ID задачи')
    description: str = Field(default=..., description='Описание задачи')
    url: str = Field(default=..., description='Ссылка')
    reward: int = Field(default=..., description='Награда за выполнение')

    class Config:
        from_attributes = True


class CategoriesOut(BaseModel):
    id: int = Field(default=..., description='ID категории')
    count_tasks: int = Field(default=0, description='Количество задач в категории')
    name: str = Field(default=..., description='Название категории')
    tasks: list[TaskOut] = Field(default=..., description='Задачи')

    class Config:
        from_attributes = True

    @field_validator('name', mode='before')
    def format_category_name(cls, v):
        if v is None:
            raise ValueError("Название категории не может быть пустым")
        if isinstance(v, Choice):
            return v.code

        return v

    @model_validator(mode='before')
    def calc_count_tasks(cls, values):
        tasks = values.get('tasks', [])
        values['count_tasks'] = len(tasks)
        return values


class TaskByUser(BaseModel):
    id: int = Field(default=..., description='ID задачи')

    class Config:
        from_attributes = True
