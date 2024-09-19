import asyncio
import logging
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest
from celery import Celery
from celery.schedules import crontab
from bot_main import bot
from database import async_session
from repository import get_tasks_by_celery, get_posts_by_celery, post_update_by_celery, \
    task_delete_by_celery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Celery(
        'tasks',
        broker='redis://redis:6379/0',
        backend='redis://redis:6379/0'
)
app.conf.timezone = 'Europe/Moscow'

loop = asyncio.get_event_loop()


def delete_message(bot, chat_id, id_message):
    try:
        bot.delete_message(chat_id=chat_id, message_id=id_message)
    except TelegramBadRequest as ex:
        pass  # логирование в файл

@app.task
def check_posts():
    session = async_session()
    try:
        today = datetime.today().date()
        posts = loop.run_until_complete(get_posts_by_celery(session))
        for post in posts:
            if post.date_expired > today:
                loop.run_until_complete(bot.send_message(chat_id=post.user_telegram,
                                                         text=f"Ваше [объявление]({post.url_message})"
                                                              f"удалено, так как истёк срок его размещения.\n"
                                                              f"Для его продления Вам необходимо будет перейти во вкладку"
                                                              f"'Мои объявления' и опубликовать его заново, либо создать новое объявление "
                                                              f"и опубликовать его "))
                chat_id = post.channel_id.split('_')[0]
                id_message = post.url_message.split('/')[4]
                id_main_message = post.url_message_main.split('/')[4]
                loop.run_until_complete(delete_message(bot, chat_id, id_message))
                if id_main_message != id_message:
                    loop.run_until_complete(delete_message(bot, chat_id, id_main_message))
                loop.run_until_complete(post_update_by_celery(session, post.id, active=False))
    finally:
        loop.run_until_complete(session.close())


@app.task
def check_tasks():
    session = async_session()
    try:
        today = datetime.today().date()
        tasks = loop.run_until_complete(get_tasks_by_celery(session))
        for task in tasks:
            if task.date_limit > today:
                loop.run_until_complete(task_delete_by_celery(session, task.id, active=False))

    finally:
        loop.run_until_complete(session.close())


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
            crontab(hour=9, minute=30),
            check_posts.s(), name='add_post-every-20-00'
    )
    sender.add_periodic_task(
            crontab(hour=10, minute=30),
            check_tasks.s(), name='add_task-every-10-30'
    )
