from pydantic import BaseModel, Field, field_validator


class Rank(BaseModel):
    id: int = Field(..., description='ID ранга')
    rank: str = Field(default=..., description='Название ранга')
    level: int = Field(default=..., description='Уровень')

    @field_validator('rank', mode='before')
    def format_transaction_date(cls, v):
        return v.name

    class Config:
        from_attributes = True


class ConditionOut(BaseModel):
    type: str = Field(default=..., description='Тип требования')
    description: str = Field(default=..., description='Описание')
    target: int = Field(default=..., description='Значение')


class RankInfoOut(BaseModel):
    id: int = Field(default=1, description='ID текущего ранга')
    rank: str = Field(default=1, description='Название ранга')
    level: int = Field(default=1, description='Уровень текущего ранга')
    conditions: list[ConditionOut]

    @field_validator('rank', mode='before')
    def format_transaction_date(cls, v):
        return v.name


class RankOutInfo(BaseModel):
    id: int = Field(..., description='ID ранга')
    rank: str = Field(default=..., description='Название ранга')
    level: int = Field(default=..., description='Уровень')
    required_coins: int = Field(default=..., description='Требуемое количество монет')

    @field_validator('rank', mode='before')
    def format_transaction_date(cls, v):
        return v.name

    class Config:
        from_attributes = True
