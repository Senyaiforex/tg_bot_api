from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ChangeCoins(BaseModel):
    amount: int = Field(gt=0, description='Количество монет')
    description: str = Field(description='Описание транзакции')
    add: bool = Field(description='Добавить или вычесть(True or False)')


class ChangeSpinners(BaseModel):
    amount: int = Field(gt=0, description='Количество спиннеров')
    add: bool = Field(description='Добавить или вычесть(True or False)')


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


class AddTransaction(BaseModel):
    from_currency: str
    from_amount: int | float
    to_currency: str
    to_amount: int | float


class HistoryChangeTransactionOut(BaseModel):
    id: int = Field(..., description='ID транзакции')
    transaction_date: datetime | str = Field(..., description='Дата транзакции')
    from_currency: str
    from_amount: int | float
    to_currency: str
    to_amount: int | float

    @field_validator('transaction_date', mode='before')
    def format_transaction_date(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%d-%m-%Y %H:%M')
        elif isinstance(v, str):
            try:
                parsed_date = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                return parsed_date.strftime('%d-%m-%Y %H:%M')
            except ValueError:
                pass
        return v

    class Config:
        from_attributes = True

a = {'from_сurrency': 'ton', 'from_amount': 100,
     'to_currency': 'stars', 'to_amount': 200}