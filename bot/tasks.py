import os
import asyncio
from contextlib import suppress, asynccontextmanager

from aiogram.types import FSInputFile
from loguru import logger
from datetime import datetime, timedelta

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.ext.asyncio import async_scoped_session

from bot_main import bot
from database import async_session
from repository import PostRepository, TaskRepository, UserRepository, SellerRepository
from bot_admin import bot as admin_bot
from models import User
from utils.bot_utils.text_static import txt_adm, txt_us
from asgiref.sync import async_to_sync

redis_password = os.getenv('REDIS_PASSWORD')

logger.add("logs/logs_celery/log_file.log",
           retention="5 days",
           rotation='21:00',
           compression="zip",
           level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | "
                  "{level: <8} | "
                  "{name}:{function}:{line} - "
                  "{message}")
app = Celery(
        'tasks',
        broker=f'redis://:{redis_password}@redis:6379/0',
        backend=f'redis://:{redis_password}@redis:6379/0'
)
app.conf.timezone = 'Europe/Moscow'

loop = asyncio.get_event_loop()

@asynccontextmanager
async def scoped_session():
    scoped_factory = async_scoped_session(
        async_session,
        scopefunc=asyncio.current_task,
    )
    try:
        async with scoped_factory() as s:
            yield s
    finally:
        await scoped_factory.remove()

# async def get_async_session() -> async_session:
#     async with async_session() as session:
#         yield session
#         await session.close()


async def delete_message(bot_instance, chat_id, id_message) -> None:
    with suppress(*(TelegramBadRequest, TelegramForbiddenError)):
        await bot_instance.delete_message(chat_id=chat_id, message_id=id_message)


async def send_message(bot_instance, chat_id, text) -> None:
    with suppress(*(TelegramBadRequest, TelegramForbiddenError)):
        await bot_instance.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def send_messages_for_admin(bot_instance, admins: list[User], text: str) -> None:
    for admin in admins:
        await send_message(bot_instance, chat_id=admin.id_telegram, text=text)


@app.task
def check_posts():
    loop.run_until_complete(work_posts())


@app.task
def check_tasks():
    loop.run_until_complete(work_tasks())


@app.task
def check_sellers():
    loop.run_until_complete(work_sellers())


@app.task
def check_and_clear_liquid():
    loop.run_until_complete(liquid_clear())


@logger.catch
async def work_tasks():
    async with scoped_session() as session:
        today = datetime.today().date()
        tasks = await TaskRepository.get_tasks_by_celery(session, today)
        admins = await UserRepository.get_admins(session)
        await TaskRepository.task_deactivate_by_celery(session, today)
        for task in tasks:
            await send_messages_for_admin(admin_bot, admins, txt_adm.task_expired.format(name=task.description,
                                                                                         url=task.url))


@logger.catch
async def work_sellers():
    async with scoped_session() as session:
        date = datetime.today().date()
        next_date = date + timedelta(days=1)
        count_subscribes = await bot.get_chat_member_count(chat_id=-1002090610085)
        count_users = await SellerRepository.get_count_users(session, date)
        count_sellers = await SellerRepository.get_count_sellers(session, date)
        difference = count_subscribes - count_users
        if difference < 0:
            difference = 0
        admins = await UserRepository.get_admins(session, True)
        date_str = date.strftime('%d-%m-%Y')
        for admin in admins:
            with suppress(*(TelegramBadRequest, TelegramForbiddenError)):
                picture = FSInputFile('static/start_pic.jpg')
                text = (f"*Статистика на {date_str}*\n"
                        f"Количество постов в группе - *{count_sellers}*\n"
                        f"Количество новых пользователей - *{difference}*")
                await admin_bot.send_photo(chat_id=admin.id_telegram,
                                           photo=picture, parse_mode='Markdown',
                                           caption=text)
        await SellerRepository.create_instance_seller(session, count_subscribes, next_date)
        date_expired = next_date - timedelta(days=14)
        await SellerRepository.sellers_clear(date_expired, session)


@logger.catch
async def liquid_clear():
    async with scoped_session() as session:
        await PostRepository.liquid_clear(session)


@logger.catch
async def work_posts():
    async with scoped_session() as session:
        today = datetime.today().date()
        posts = await PostRepository.get_posts_by_celery(session, today)
        for post in posts:
            await send_message(bot, chat_id=post.user_telegram,
                               text=txt_us.post_expired.format(url=post.url_message))
            try:
                chat_id = post.channel_id.split('_')[0]
                id_message = post.url_message.split('/')[4]
                id_main_message = post.url_message_main.split('/')[4]
            except AttributeError as ex:
                pass
            else:
                await delete_message(bot, chat_id, id_message)
                if id_main_message != id_message:
                    await delete_message(bot, chat_id, id_main_message)
                if post.url_message_free and post.url_message_free != post.url_message:
                    id_message_free = post.url_message_free.split('/')[4]
                    await delete_message(bot, chat_id, id_message_free)
            await PostRepository.post_update_by_celery(session, post.id, active=False)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
            crontab(hour=21, minute=58),
            check_posts.s(), name='check_post-every-16-00'
    )
    sender.add_periodic_task(
            crontab(hour=10, minute=30),
            check_tasks.s(), name='check_task-every-10-30'
    )
    sender.add_periodic_task(
            crontab(hour=23, minute=59),
            check_sellers.s(), name='clear_sellers-every-day'
    )
    sender.add_periodic_task(
            crontab(hour=0, minute=0, day_of_month='1'),
            check_and_clear_liquid.s(), name='monthly_task-every-1st'
    )
