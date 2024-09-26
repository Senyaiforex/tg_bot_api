from pydantic import BaseModel, Field


class LiquidOut(BaseModel):
    need: int = Field(default=..., ge=0, description='Сколько необходимо публикаций')
    current: int = Field(default=..., ge=0, description='Текущее количество публикаций')
    percent: str = Field(default=..., description='Процентное соотношение со знаком +-')


class PlanLiquidOut(BaseModel):
    type_liquid: str = Field(default=..., description='Тип ликвидности')
    data: LiquidOut