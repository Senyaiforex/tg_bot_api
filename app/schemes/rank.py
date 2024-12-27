from pydantic import BaseModel, Field, field_validator, root_validator, model_validator

dict_rank_names = {
        "stone": "Лига исследователей",
        "copper": "Лига Выгодных Сделок",
        "silver": "Лига Удачных Покупок",
        "gold": "Лига Цифровой Торговли",
        "platinum": "Лига Лояльных покупателей",
        "diamond": "Лига Бонусных Возможностей",
        "sapphire": "Лига Звездных Сделок",
        "ruby": "Лига Топ-Маркетплейсов",
        "amethyst": "Лига Экспертов Маркетплейсов",
        "morganite": "Лига Покупательской Славы",
}


class Rank(BaseModel):
    id: int = Field(..., description='ID ранга')
    rank: str = Field(default=..., description='Название ранга')
    level: int = Field(default=..., description='Уровень')
    rank_name: str = Field(default=..., description='Название ранга на русском')

    @field_validator('rank', mode='before')
    def format_rank(cls, v):
        return v.name

    @model_validator(mode='before')
    def set_rank_name(cls, values):
        rank = values.get("rank").name
        values["rank_name"] = dict_rank_names[rank]
        return values

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
    rank_name: str = Field(default=..., description='Название ранга на русском')

    @field_validator('rank', mode='before')
    def format_rank(cls, v):
        return v.name

    @model_validator(mode='before')
    def set_rank_name(cls, values):
        rank = values.get("rank").name
        values["rank_name"] = dict_rank_names[rank]
        return values

class RankOutInfo(BaseModel):
    id: int = Field(..., description='ID ранга')
    rank: str = Field(default=..., description='Название ранга')
    level: int = Field(default=..., description='Уровень')
    required_coins: int = Field(default=..., description='Требуемое количество монет')
    rank_name: str = Field(default=..., description='Название ранга на русском')

    @field_validator('rank', mode='before')
    def format_rank(cls, v):
        return v.name

    @model_validator(mode='before')
    def set_rank_name(cls, values):
        rank = values.get("rank").name
        values["rank_name"] = dict_rank_names[rank]
        return values

    class Config:
        from_attributes = True
