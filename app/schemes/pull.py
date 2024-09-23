from pydantic import BaseModel, Field


class PullOut(BaseModel):
    type_pull: str = Field(default=..., description='Тип пула')
    size: int = Field(default=..., description='Максимальное значение')
    current_size: int = Field(default=0, description='Текущее значение')
    percent: int = Field(default=0, description='На сколько заполнен пулл в %')