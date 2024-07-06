from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.params import Path, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from repository import *
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import engine, async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
    )


app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Разрешить все домены
        allow_credentials=True,
        allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
        allow_headers=["*"],  # Разрешить все заголовки
)
# API_KEY нужен для того, чтобы доступ к API имел только тот клиент, который в
# параметре запроса указывает нужный api_key
API_KEY = "ars"


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def get_api_key(api_key: str = Header(..., alias='api_key')):
    """
    Функция для проверки соответствия ключа API, передаваемого в заголовке
    :param api_key: API ключ, передаваемый в заголовке
    :return: None
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")


@app.get("/api/get_user_info/{id_telegram}")
async def get_user(id_telegram: int = Path(..., title='ID пользователя телеграм'),
                   session=Depends(get_async_session),
                   api_key: str = Header(..., alias="api_key")):
    """
    • Описание: Возвращает информацию о пользователе.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ api_key (заголовок, str): API ключ для аутентификации.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию о пользователе (id_telegram, user_name, count_token, count_pharmd).\n
        ◦ Пример:\n
        ◦ { "id_telegram": 123456, "user_name": "example_user", "count_token": 0, "count_pharmd": 65000 }\n
    """
    get_api_key(api_key)
    user = await get_user_by_telegram_id(id_telegram, session)
    user_data = schemes.CreateUser.from_orm(user)

    return JSONResponse(content=user_data.dict())


@app.get("/api/get_count_tokens/{id_telegram}")
async def get_tokens(id_telegram: int = Path(..., title='ID пользователя телеграм'),
                     session=Depends(get_async_session),
                     api_key: str = Header(..., alias="api_key")):
    """
    • Описание: Возвращает количество токенов у пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ api_key (заголовок, str): API ключ для аутентификации.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий количество токенов.\n
        ◦ Пример:\n
        ◦ { "count_tokens": 100 }
    """
    get_api_key(api_key)
    user = await get_user_by_telegram_id(id_telegram, session)
    return JSONResponse(content={'count_tokens': user.count_tokens})


@app.get("/api/get_count_pharmd/{id_telegram}")
async def get_pharmd(id_telegram: int = Path(..., title='ID пользователя телеграм'),
                     session=Depends(get_async_session),
                     api_key: str = Header(..., alias="api_key")):
    """
    • Описание: Возвращает количество фарма у пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ api_key (заголовок, str): API ключ для аутентификации.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий количество фарма.\n
        ◦ Пример:\n
        ◦ { "count_pharmd": 65000 }
    """
    get_api_key(api_key)
    user = await get_user_by_telegram_id(id_telegram, session)
    return JSONResponse(content={'count_pharmd': user.count_pharmd})


@app.post('/api/create_user')
async def create_user(user: schemes.CreateUser,
                      session: AsyncSession = Depends(get_async_session),
                      api_key: str = Header(..., alias='api_key')):
    """
    • Описание: Создает нового пользователя в базе данных.\n
    • Параметры:\n
        ◦ user (тело запроса, схема CreateUser): Данные пользователя.\n
        ◦ api_key (заголовок, str): API ключ для аутентификации.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию о созданном пользователе.\n
        ◦ Пример:\n
        ◦ { "id_telegram": 123456, "user_name": "new_user", "count_token": 0, "count_pharmd": 65000 }\n
    """
    get_api_key(api_key)
    new_user = await base_create_user(user, session)
    return JSONResponse(new_user.dict())


@app.put('/api/change_token')
async def change_token(data_new: schemes.ChangeToken,
                       session: AsyncSession = Depends(get_async_session),
                       api_key: str = Header(..., alias='api_key')):
    """
    • Описание: Изменяет количество токенов у пользователя.\n
    • Параметры:\n
        ◦ data_new (тело запроса, схема ChangeToken): Данные для изменения токенов.\n
        ◦ api_key (заголовок, str): API ключ для аутентификации.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий обновленную информацию о токенах пользователя.\n
        ◦ Пример: { "id_telegram": 123456, "count_tokens": 150 }
    """
    get_api_key(api_key)
    user = await change_tokens_by_id(data_new.id_telegram, data_new.amount, data_new.add, session)
    return JSONResponse(content={'id_telegram': user.id_telegram, 'count_tokens': user.count_tokens})


@app.put('/api/change_pharmd')
async def change_pharmd(data_new: schemes.ChangeToken,
                        session: AsyncSession = Depends(get_async_session),
                        api_key: str = Header(..., alias='api_key')):
    """
    • Описание: Изменяет количество фарма у пользователя.\n
    • Параметры:\n
        ◦ data_new (тело запроса, схема ChangeToken): Данные для изменения фарма.\n
        ◦ api_key (заголовок, str): API ключ для аутентификации.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий обновленную информацию о фарме пользователя.\n
        ◦ Пример:\n
        ◦ { "id_telegram": 123456, "count_pharmd": 70000 }\n
    """
    get_api_key(api_key)
    user = await change_pharmd_by_id(data_new.id_telegram, data_new.amount, data_new.add, session)
    return JSONResponse(content={'id_telegram': user.id_telegram, 'count_pharmd': user.count_pharmd})


@app.delete('/api/delete_user')
async def delete_user(user: schemes.DeleteUser,
                      session: AsyncSession = Depends(get_async_session),
                      api_key: str = Header(..., alias='api_key')):
    """
    • Описание: Удаляет пользователя из базы данных.\n
    • Параметры:\n
        ◦ user (тело запроса, схема DeleteUser): Данные пользователя для удаления.\n
        ◦ api_key (заголовок, str): API ключ для аутентификации.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, указывающий на успешное удаление.\n
        ◦ Пример:\n
        ◦ { "detail": "User deleted" }

    """
    get_api_key(api_key)
    user = await get_user_by_telegram_id(user.id_telegram, session)
    await session.delete(user)
    await session.commit()
    return JSONResponse(content={"detail": "User deleted"})
