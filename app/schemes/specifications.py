from pydantic import BaseModel, Field


class ChangeCoins(BaseModel):
    amount: int = Field(gt=0, description='Количество монет')
    description: str = Field(description='Описание транзакции')
    add: bool = Field(description='Добавить или вычесть(True or False)')

class ChangeSpinners(BaseModel):
    amount: int = Field(gt=0, description='Количество спиннеров')
    add: bool = Field(gt=0, description='Добавить или вычесть(True or False)')

class ChangePharmd(BaseModel):
    amount: int = Field(gt=0, description='Количество фарма')
    add: bool = Field(description='Добавить или вычесть(True or False)')


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