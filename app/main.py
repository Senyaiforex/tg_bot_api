from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.params import Path, Annotated, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .repository import *
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, async_session, Base
from .schemes import UserIn, UserOut, DeleteUser, ChangeCoins, ChangePharmd, HistoryTransactionOut, HistoryTransactionList, TopUsers


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan, title="Buyer Bot API")


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
    )


app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],  # Разрешить все домены
        allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
        allow_headers=["*"],  # Разрешить все заголовки
)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.get("/api/get_user_info/{id_telegram}", response_model=UserOut)
async def get_user(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                   session=Depends(get_async_session)):
    """
    • Описание: Возвращает информацию о пользователе.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию о пользователе.\n
    """
    user = await get_user_by_telegram_id(id_telegram, session)
    return user


@app.get("/api/friends/{id_telegram}", response_model=list[dict])
async def get_user_friends(id_telegram: int, session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Получить всех друзей пользователя \n
    • Параметры:\n
        ◦ telegram_id: Telegram  ID пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию по каждому другу. Username, Количество токенов, уровень.\n

    """
    friends = await get_friends(id_telegram, session)

    if friends is None:
        raise HTTPException(status_code=404, detail="User not found or no friends")

    return friends


@app.get("/api/get_count_coins/{id_telegram}")
async def get_coins(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                    session=Depends(get_async_session)):
    """
    • Описание: Возвращает количество токенов у пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий количество токенов.\n
    """
    user = await get_user_by_telegram_id(id_telegram, session)
    return JSONResponse(content={'count_coins': f'{user.count_coins}'},
                        headers={'Content-Type': 'application/json'})


@app.get("/api/get_top_users", response_model=TopUsers)
async def get_top_users(limit: int = Query(default=10, description='Количество'),
                        session=Depends(get_async_session)):
    """
    • Описание: Возвращает топ пользователей отсортированных по count_coins.\n
    • Параметры:\n
        ◦ limit (параметр запроса, int): Количество пользователей из топа.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий массив с топом пользователей.\n
    """
    users = await get_users_limit(limit, session)
    return TopUsers(top_users=users)


@app.get("/api/get_count_pharmd/{id_telegram}")
async def get_pharmd(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                     session=Depends(get_async_session)):
    """
    • Описание: Возвращает количество фарма у пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий количество фарма.\n
    """
    user = await get_user_by_telegram_id(id_telegram, session)
    return JSONResponse(content={'count_pharmd': f'{user.count_pharmd}'}, headers={'Content-Type': 'application/json'})


@app.get("/api/get_transactions/{id_telegram}", response_model=HistoryTransactionList)
async def get_transactions(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                           limit: int = Query(default=30, description='Количество транзакций', gt=0),
                           session=Depends(get_async_session)):
    """
    • Описание: Возвращает все транзакции пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ limit (параметр запроса, int): Лимит количества транзакций.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий все транзакции пользователя.\n
    """
    transactions = await get_transactions_by_id(id_telegram, limit, session)
    formatted_transactions = [
            HistoryTransactionOut(
                    id=txn.id,
                    change_amount=txn.change_amount,
                    description=txn.description,
                    transaction_date=txn.transaction_date.strftime('%d-%m-%Y %H:%M')
            )
            for txn in transactions
    ]

    return HistoryTransactionList(transactions=formatted_transactions)


@app.post('/api/create_user', response_model=UserOut)
async def create_user(user: UserIn,
                      session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Создает нового пользователя в базе данных.\n
    • Параметры:\n
        ◦ user (тело запроса, схема User): Данные пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию о созданном пользователе.\n
    """
    new_user = await base_create_user(user, session)
    user_dict = {
            "id_telegram": new_user.id_telegram,
            "user_name": new_user.user_name,
            "count_coins": new_user.count_coins,
            "count_pharmd": new_user.count_pharmd
    }
    return JSONResponse(user_dict)


@app.patch('/api/change_coins/{id_telegram}')
async def change_coins(id_telegram: int, data_new: ChangeCoins,
                       session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Изменяет количество токенов у пользователя.\n
    • Параметры:\n
        ◦ id_telegram, amount, add (тело запроса, схема ChangeToken): Данные для изменения токенов.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий обновленную информацию о токенах пользователя.\n
    """
    user = await change_coins_by_id(id_telegram, data_new.amount, data_new.add, session)
    return JSONResponse(content={'id_telegram': f'{user.id_telegram}', 'count_coins': f'{user.count_coins}'})


@app.patch('/api/change_pharmd/{id_telegram}')
async def change_pharmd(id_telegram: int, data_new: ChangePharmd,
                        session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Изменяет количество фарма у пользователя.\n
    • Параметры:\n
        ◦ id_telegram, amount, add (тело запроса, схема ChangeToken): Данные для изменения фарма.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий обновленную информацию о фарме пользователя.\n
    """
    user = await change_pharmd_by_id(id_telegram, data_new.amount, data_new.add, session)
    return JSONResponse(content={'id_telegram': f'{user.id_telegram}', 'count_pharmd': f'{user.count_pharmd}'})


@app.delete('/api/delete_user')
async def delete_user(user: DeleteUser,
                      session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Удаляет пользователя из базы данных.\n
    • Параметры:\n
        ◦ id_telegram (тело запроса, схема DeleteUser): Данные пользователя для удаления.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, указывающий на успешное удаление.\n

    """
    user = await get_user_by_telegram_id(user.id_telegram, session)
    await session.delete(user)
    await session.commit()
    return JSONResponse(content={"detail": "User deleted"})


def main():
    config = uvicorn.Config(app, host='127.0.0.1', port=8000, log_level="info")
    server = uvicorn.Server(config)
    try:
        server.run()
    except KeyboardInterrupt:
        print("----Приложение было принудительно остановлено----")


if __name__ == '__main__':
    main()
