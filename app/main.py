import os
import sys
import asyncio
from sys import prefix
from fastapi.encoders import jsonable_encoder
from loguru import logger
import aiohttp
import uvicorn
from redis import asyncio as aioredis
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from models import users_tasks
from models.tasks import CategoryTask
from repository.rank import RankRepository
from repository.users import TransactionRepository
from utils.app_utils import check_task_complete, create_data_tasks
from fastapi.params import Path, Annotated, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Request, HTTPException
from repository import UserRepository, PostRepository, TaskRepository, PullRepository, SellerRepository
from database import engine, async_session, Base
from fixtures import *
from schemes import *
from utils.app_utils.utils import create_data_posts, create_data_pull, create_data_liquid, get_friend_word, \
    check_ton_info
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

DEBUG = os.getenv("DEBUG")
redis_password = os.getenv("REDIS_PASSWORD")
logger.add("logs/log_file.log",
           retention=6, level="DEBUG",
           rotation='20:00', compression="zip",
           format="{time:MMMM D, YYYY - HH:mm:ss} {level} ---- {message}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://:{redis_password}@redis-app:6379", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="app-cache")
    await FastAPICache.clear()
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        await create_ranks(session)
        await create_categories(session)
        await create_liquid(session)
        await create_pull(session)
        await create_bank(session)
        await create_admins(session)
        await create_sellers(session)
    yield
    await engine.dispose()
    await redis.close()


app = FastAPI(lifespan=lifespan, title="Buyer Bot API")


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    logger.error(exc, exc_info=True)
    return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
    )


@cache()
async def get_cache():
    return 1


origins = [
        os.getenv("SITE_NAME"),
]
app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=origins,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
        allow_headers=["Content-Type", "Ngrok-Skip-Browser-Warning", "User-Agent",
                       "Connection", "Set-Cookie", "Access-Control-Allow-Origin"
                                                   "Access-Control-Allow-Headers", "Access-Control-Allow-Methods"],
)


async def get_async_session() -> async_session:
    async with async_session() as session:
        yield session
        await session.close()


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
    user = await UserRepository.get_user_by_telegram_id(id_telegram, session)
    return user


@app.get("/api/get_rank_info/{id_telegram}", response_model=RankInfoOut)
async def get_rank_info(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                        session=Depends(get_async_session)):
    """
    • Описание: Возвращает информацию о текущем ранге пользователя и сколько
                необходимо набрать монет и выолнить задач для получения следующего ранга.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию о текущем ранге пользователя и
            необходимых условий для получения следующего ранга.\n
    """
    user = await UserRepository.get_user_by_telegram_id(id_telegram, session)
    rank_instance_dict = {True: await RankRepository.get_next_rank(user.rank.id, session),
                          False: user.rank}
    next_rank = rank_instance_dict[user.rank.id < 100]
    friend_word = await get_friend_word(next_rank.required_friends)
    dict_condition = {
            next_rank.required_coins: (f"Заработать {next_rank.required_coins:,} монет"
                                       .replace(',', ' '), 'coins'),
            next_rank.required_friends: (f"Пригласить {next_rank.required_friends} " + friend_word,
                                         'friends'),
            next_rank.required_tasks: (f"Выполнить {next_rank.required_tasks} задач",
                                       'tasks')
    }
    conditions = [ConditionOut(type=value[1],
                               description=value[0],
                               target=key) for key, value in dict_condition.items()]
    return RankInfoOut(**user.rank.__dict__,
                       conditions=conditions)


@app.get("/api/friends/{id_telegram}", response_model=list[dict])
async def get_user_friends(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                           session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Получить всех друзей пользователя \n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию по каждому другу. Username, Количество токенов, уровень.\n

    """
    friends = await UserRepository.get_friends(id_telegram, session)
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
    coins = await UserRepository.get_count_coins(session, id_telegram)
    return JSONResponse(content={'count_coins': f'{coins}'})


@app.get("/api/get_top_users", response_model=list[dict])
async def get_top_users(limit: int = Query(default=10, description='Количество'),
                        offset: int = Query(default=0, description='Пагинация'),
                        session=Depends(get_async_session)):
    """
    • Описание: Возвращает топ пользователей отсортированных по total_coins
                (общему количеству заработанных монет).\n
    • Параметры:\n
        ◦ limit (параметр запроса, int): Количество пользователей из топа.\n
        ◦ offset (параметр запроса, int): Пагинация.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий массив с топом пользователей.\n
    """
    users = await UserRepository.get_users_limit(limit, offset, session)
    list_users = [{'id_telegram': user.id_telegram,
                   'username': user.user_name,
                   'count_coins': user.total_coins,
                   'rank': user.rank.rank.name,
                   'level': user.rank.level} for user in users]
    return JSONResponse(list_users, status_code=200)


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
    pharmd = await UserRepository.get_count_pharmd(session, id_telegram)
    return JSONResponse(content={'count_pharmd': f'{pharmd}'})


@app.get("/api/get_transactions/{id_telegram}", response_model=list[HistoryTransactionOut])
async def get_transactions(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                           limit: int = Query(default=30, description='Количество транзакций', gt=0),
                           offset: int = Query(default=0, description='Пагинация'),
                           session=Depends(get_async_session)):
    """
    • Описание: Возвращает все транзакции пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ limit (параметр запроса, int): Лимит количества транзакций.\n
        ◦ offset (параметр запроса, int): Пагинация.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий все транзакции пользователя.\n
    """
    transactions = await UserRepository.get_transactions_by_id(id_telegram, limit, offset, session)
    return transactions


@app.get("/api/crypto_info/{id_telegram}")
@cache(expire=3600)
async def get_ton_info(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                       session=Depends(get_async_session)):
    """
    • Описание: Возвращает информацию о токеномике на проекте.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию о токеномике.\n
    """
    all_count_tokens = 100_000_000
    price, market_cap, usdt_to_ton, usdt_to_rub = await check_ton_info()
    user = await UserRepository.get_user_tg(id_telegram, session)
    all_vouchers = await UserRepository.get_sum_vouchers(session)
    user_share_project = round(user.vouchers / all_count_tokens * 100, 4)
    ton_to_usdt = price
    ton_to_rub = ton_to_usdt * usdt_to_rub * 1.1
    voucher_to_usdt = 0.02
    voucher_to_ton = 0.02 / ton_to_usdt
    stages = [{"text": "1 этап: 10 000 000 токенов по $ 0.02",
               "isActive": False,
               "progress": 0},
              {"text": "2 этап: 10 000 000 токенов по $ 0.04",
               "isActive": False,
               "progress": 0},
              {"text": "3 этап: 10 000 000 токенов по $ 0.06",
               "isActive": False,
               "progress": 0},
              ]
    if all_vouchers <= 10_000_000:
        stages[0]["isActive"] = True
        stages[0]["progress"] = round((all_vouchers / 10_000_000 * 100), 2)
    elif 10_000_000 < all_vouchers <= 20_000_000:
        stages[1]["isActive"] = True
        stages[1]["progress"] = round(((all_vouchers - 10_000_000) / 10_000_000 * 100), 2)
    elif 20_000_000 < all_vouchers <= 30_000_000:
        stages[2]["isActive"] = True
        stages[2]["progress"] = round(((all_vouchers - 20_000_000) / 10_000_000 * 100), 2)
    result_dict = {"ton": {"ton_to_usdt": ton_to_usdt,
                           "ton_to_rub": ton_to_rub,
                           "ton_market_cap": market_cap},
                   "voucher": {"voucher_to_usdt": voucher_to_usdt,
                                "voucher_to_ton": voucher_to_ton},
                   "stars": {"stars_to_ton": 0.034,
                             "stars_to_rub": 2},
                   "coins": {"coins_to_ton": 0.00002,
                             "coins_to_stars": 0.0075},
                   "user_pull": {"all_tokens": all_count_tokens,
                                 "share_in_project": user_share_project},
                   "stages": stages}
    return JSONResponse(content=result_dict)


@app.get("/api/history_transactions/{id_telegram}", response_model=list[HistoryChangeTransactionOut])
async def get_transactions(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                           limit: int = Query(default=30, description='Количество транзакций', gt=0),
                           offset: int = Query(default=0, description='Пагинация'),
                           session=Depends(get_async_session)):
    """
    • Описание: Возвращает все обменные транзакции пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ limit (параметр запроса, int): Лимит количества транзакций.\n
        ◦ offset (параметр запроса, int): Пагинация.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий все обменные транзакции пользователя.\n
    """
    transactions = await TransactionRepository.get_change_transactions_by_id(id_telegram, limit, offset, session)
    return transactions


@app.get('/api/check_task_complete/{id_telegram}/{id_task}')
@logger.catch
async def get_task_status(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                          id_task: Annotated[int, Path(description="ID задачи", gt=0)],
                          session=Depends(get_async_session)):
    """
    • Описание: Метод для проверки, выполнена ли задача пользователем\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ id_task (параметр пути, int): ID задачи.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, {'completed': True of False}\n
    """
    task_complete = await check_task_complete(id_telegram, id_task)
    return JSONResponse(content={'complete': task_complete})


@app.get('/api/tasks/{id_telegram}/', response_model=list[CategoriesOut])
@logger.catch
async def get_tasks(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                    session=Depends(get_async_session)):
    """
    • Описание: Метод для получения всех задач, сгруппированных по категориям.
                Также в ответе содержатся задачи, выполненные пользователем - completed\n
    • Параметры:\n
        ◦ нет\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий все задачи\n
    """
    categories = await create_data_tasks(TaskOut, CategoriesOut, id_telegram, session)
    return categories


@app.get('/api/count_members')
@cache(expire=1800)
async def get_count_members(session=Depends(get_async_session)):
    """
    • Описание: Метод для получения количества продавцов и покупателей
    • Параметры:\n
        ◦ нет\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий количество продавцов sellers и покупателей buyers
    """
    date_today = datetime.today().date()
    sellers = await SellerRepository.count_all_sellers(session)
    async with aiohttp.ClientSession() as session:
        response = await session.get('http://telegram_bot:8443/count_subscribed')
        content = await response.json()
        return JSONResponse(content={'sellers': sellers,
                                     'buyers': int(content.get('count'))})


@app.get('/api/count_posts_by_type', response_model=list[PostsByType])
@logger.catch
@cache(expire=1800)
async def get_count_posts_by_type(session=Depends(get_async_session)):
    """
    • Описание: Метод для получения количества опубликованных постов
      за последний месяц в зависимости от их типа
    • Параметры:\n
        ◦ нет\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий количество опубликованных постов
    """
    date_today = datetime.today().date()
    posts_today_count = await PostRepository.get_count_post_by_time(session, date_today)
    data = await create_data_posts(session, date_today, posts_today_count[0])

    return [PostsByType(**inst) for inst in data]


@app.get('/api/ranks_list', response_model=list[RankOutInfo])
@cache(expire=12 * 10 ** 5)
async def get_all_ranks(session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Метод для получения информации обо всех рангах
    • Параметры:\n
        ◦ нет\n
    • Ответ:\n
        'Параметры ранга'
            id - ID ранга
            rank - Название ранга
            level - Уровень ранга
            required_coins - требуемое количество монет
        ◦ 200 OK: JSON объект, содержащий информацию о всех рангах
    """
    ranks = await RankRepository.get_all_ranks(session)
    return ranks


@app.get('/api/pulls_info', response_model=list[PullOut])
@logger.catch
@cache(expire=900)
async def pull_info(session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Метод для получения информации о пулле
    • Параметры:\n
        ◦ нет\n
    • Ответ:\n
        'Параметры пулла'
            type_pull - тип пулла
            size - максимальный размер пулла
            current_size - текущий пулл
            percent - отношение текущего пула к максимальному в %
        ◦ 200 OK: JSON объект, содержащий информацию об общем пулле
    """

    pull = await PullRepository.get_pull(session)
    dict_data = await create_data_pull(pull)
    list_pulls = [PullOut(type_pull=key,
                          size=value[0],
                          current_size=value[1],
                          percent=value[2]) for key, value in dict_data.items()]
    return list_pulls


@app.get('/api/plan_info', response_model=list[PlanLiquidOut])
@cache(expire=1800)
async def plan_info(session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Метод для получения информации пуле ликвидности постов
    • Параметры:\n
        ◦ нет\n
    • Ответ:\n
        'Параметры пулла'
            type_liquid - тип ликвидности(всего постов, бесплатных, платных)
            data - информация о количестве и соотношении
            need - сколько необходимо постов
            current - сколько сейчас есть постов
            percent - отношение текущего количество к нужному в %
        ◦ 200 OK: JSON объект, содержащий информацию о пуле ликвидности
    """

    dict_data = await create_data_liquid(session)
    plan_posts_liquid = [PlanLiquidOut(type_liquid=key,
                                       data=LiquidOut(**value)) for key, value in dict_data.items()]
    return plan_posts_liquid


@app.get("/api/get_total_coins")
@cache(expire=1800)
async def get_total_all_coins(session=Depends(get_async_session)):
    """
    • Описание: Возвращает количество монет в обороте в приложении.\n
    • Параметры:\n
        ◦ Нет
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий общее количество монет.\n
    """
    coins = await UserRepository.get_total_coins(session)
    return JSONResponse(content={'total_all_coins': f'{coins}'})


@app.post('/api/create_user', response_model=BaseUser)
async def create_user(user: UserIn,
                      session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Создает нового пользователя в базе данных.\n
    • Параметры:\n
        ◦ user (тело запроса, схема User): Данные пользователя.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий информацию о созданном пользователе.\n
    """
    new_user = await UserRepository.base_create_user(user, session)
    return new_user


@app.post('/api/add_transaction/{id_telegram}/')
async def add_change_transaction(id_telegram: Annotated[int, Path(description="Telegram ID пользователя", gt=0)],
                                 transaction: AddTransaction,
                                 session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Создание новой транзакции обмена валюты в базе данных.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ from_сurrency, from_amount, to_currency, to_amount (тело запроса, схема AddTransaction):
        Данные для создания обменной транзакции.\n
    • Ответ:\n
        ◦ 200 OK.\n
    """
    transaction = await TransactionRepository.create_transaction(session, id_telegram,
                                                                 transaction.from_currency,
                                                                 transaction.from_amount,
                                                                 transaction.to_currency,
                                                                 transaction.to_amount)
    user = await UserRepository.get_user_tg(id_telegram, session)
    if transaction.to_currency == 'coins':
        await user.update_count_coins(session, transaction.to_amount, "Покупка монет")
    elif transaction.to_currency == 'vouchers':
        user.vouchers += transaction.to_amount
        await session.commit()
    elif transaction.to_currency == 'stars' and transaction.from_amount == 'ton':
        async with aiohttp.ClientSession() as session:
            text_admin = (f"*Покупка валюты за {transaction.from_amount} TON*\n "
                          f"Telegram ID - {user_id}  никнейм - @{user_name}\n\n"
                          f"Тип валюты - *Telegram Stars*\n"
                          f"Количество - *{transaction.to_amount}*")
            data = {'user_id': user.id_telegram, 'username': user.user_name,
                    'text': text_admin}
            response = await session.post('http://telegram_bot:8443/send_admins',
                                          json=data)
    return transaction


@app.patch('/api/change_coins/{id_telegram}')
async def change_coins(id_telegram: int, data_new: ChangeCoins,
                       session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Изменяет количество монет у пользователя.\n
    • Параметры:\n
        ◦ id_telegram (параметр пути, int): Telegram ID пользователя.\n
        ◦ amount, add, description (тело запроса, схема ChangeToken): Данные для изменения монет.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий обновленную информацию о количестве монет пользователя.\n
    """
    user = await UserRepository.change_coins_by_id(id_telegram, data_new.amount, data_new.add,
                                                   data_new.description, session)
    type_pull = 'current_farming' if data_new.description == 'Farming' else "current_coins"
    if data_new.add:
        await PullRepository.update_pull(session, data_new.amount, type_pull)
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
    user = await UserRepository.change_pharmd_by_id(id_telegram, data_new.amount, data_new.add, session)
    if data_new.add:  # # # Здесь сделать изменение пулла фарма если description=farming
        await PullRepository.update_pull(session, data_new.amount, "current_farming")
    return JSONResponse(content={'id_telegram': f'{user.id_telegram}', 'count_pharmd': f'{user.count_pharmd}'})


@app.patch('/api/change_spinners/{id_telegram}')
async def change_spinners(id_telegram: int, data_new: ChangeSpinners,
                          session: AsyncSession = Depends(get_async_session)):
    """
    • Описание: Изменяет количество спиннеров у пользователя.\n
    • Параметры:\n
        ◦ id_telegram, amount, add (тело запроса, схема ChangeSpinners): Данные для изменения спиннеров.\n
    • Ответ:\n
        ◦ 200 OK: JSON объект, содержащий обновленную информацию о количестве спиннеров пользователя.\n
    """
    user = await UserRepository.change_spinners_by_id(id_telegram, data_new.amount, data_new.add, session)
    return JSONResponse(content={'id_telegram': f'{user.id_telegram}', 'spinners': f'{user.spinners}'})


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
    user = await UserRepository.get_user_by_telegram_id(user.id_telegram, session)
    await session.delete(user)
    await session.commit()
    return JSONResponse(content={"detail": "User deleted"})


@app.delete("/api/cache-clear")
async def clear_cache():
    await FastAPICache.clear()
    return {"message": "Cache cleared"}


# def main():
#     config = uvicorn.Config(app, host="0.0.0.0", port=8000, workers=4, log_level="info")
#     server = uvicorn.Server(config)
#     try:
#         server.run()
#     except KeyboardInterrupt:
#         print("----Приложение было принудительно остановлено----")


if __name__ == "__main__":
    main()
