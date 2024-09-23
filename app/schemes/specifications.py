from pydantic import BaseModel

class ChangeCoins(BaseModel):
    amount: int
    description: str
    add: bool

class ChangeSpinners(BaseModel):
    amount: int
    add: bool

class ChangePharmd(BaseModel):
    amount: int
    add: bool


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