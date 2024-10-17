import asyncio
from loguru import logger
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from celery import Celery
from celery.schedules import crontab
from bot_main import bot
from database import async_session
from repository import PostRepository, TaskRepository, UserRepository, SellerRepository
from bot_admin import bot as admin_bot
from models import User
from utils.bot_utils.text_static import txt_adm, txt_us

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
        broker='redis://redis:6379/0',
        backend='redis://redis:6379/0'
)
app.conf.timezone = 'Europe/Moscow'

loop = asyncio.get_event_loop()


async def get_async_session() -> async_session:
    async with async_session() as session:
        yield session
        await session.close()


async def delete_message(bot_instance, chat_id, id_message) -> None:
    try:
        await bot_instance.delete_message(chat_id=chat_id, message_id=id_message)
    except (TelegramBadRequest, TelegramForbiddenError) as ex:
        pass


async def send_message(bot_instance, chat_id, text) -> None:
    try:
        await bot_instance.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
    except (TelegramBadRequest, TelegramForbiddenError) as ex:
        pass


async def send_messages_for_admin(bot_instance, admins: list[User], text: str) -> None:
    for admin in admins:
        await send_message(bot_instance, chat_id=admin.id_telegram, text=text)


@app.task
def check_posts():
    asyncio.run(work_posts())


@app.task
def check_tasks():
    asyncio.run(work_tasks())


@app.task
def check_sellers():
    asyncio.run(work_sellers())


@app.task
def check_and_clear_liquid():
    asyncio.run(liquid_clear())


@logger.catch
async def work_tasks():
    async for session in get_async_session():
        today = datetime.today().date()
        tasks = await TaskRepository.get_tasks_by_celery(session, today)
        admins = await UserRepository.get_admins(session)
        for task in tasks:
            await send_messages_for_admin(admin_bot, admins, txt_adm.task_expired.format(name=task.description,
                                                                                         url=task.url))
            await TaskRepository.task_delete_by_celery(session, task.id)


@logger.catch
async def work_sellers():
    async for session in get_async_session():
        await SellerRepository.sellers_clear(session)


@logger.catch
async def liquid_clear():
    async for session in get_async_session():
        await PostRepository.liquid_clear(session)


@logger.catch
async def work_posts():
    async for session in get_async_session():
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
            crontab(hour=21, minute=53),
            check_posts.s(), name='check_post-every-16-00'
    )
    sender.add_periodic_task(
            crontab(hour=10, minute=30),
            check_tasks.s(), name='check_task-every-10-30'
    )
    sender.add_periodic_task(
            crontab(hour=0, minute=0),
            check_sellers.s(), name='clear_sellers-every-day'
    )
    sender.add_periodic_task(
            crontab(hour=0, minute=0, day_of_month='1'),
            check_and_clear_liquid.s(), name='monthly_task-every-1st'
    )
