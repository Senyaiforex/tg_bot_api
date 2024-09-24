from datetime import datetime, timedelta

from celery.states import state

import aiohttp_cors
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from bot_main import check_task_complete, public_post_in_channel, bot
import logging
from bot_admin import bot as bot_admin
from database import async_session
from repository import OrderRepository, PostRepository
from utils.bot_utils.messages import send_messages_for_admin
from utils.bot_utils.util import create_text_for_post

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def send_message(chat_id, text, url=None):
    """
    Отправляет сообщение в чат
    """
    keyboard = None if not url else InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Посмотреть', url=url)]]
    )
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

    except TelegramBadRequest as ex:
        pass  # логирование в файл


async def delete_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        return True
    except TelegramBadRequest as ex:
        return False


async def get_count_subscribed(request):
    """
    Получает количество подписчиков
    """
    try:
        count = await bot.get_chat_member_count(chat_id=-1002090610085) - 5
    except TelegramBadRequest as ex:
        logger.error(ex)
        count = 1929
    return web.json_response({'count': count}, status=200)


async def check_task(request):
    """
    Проверка, что задание выполнено пользователем
    """
    telegram_id = request.match_info.get('telegram_id')
    task_id = request.match_info.get('task_id')
    complete = await check_task_complete(telegram_id, task_id)
    response_data = {'complete': complete}
    return web.json_response(response_data)


async def delete_mes(request):
    """
    Удалить сообщение бота
    """
    chat_id = request.match_info.get('chat_id')
    id_message = request.match_info.get('id_message')
    complete = await delete_message(chat_id, id_message)
    response_data = {'complete': complete}
    if complete:
        status = 200
    else:
        status = 204
    return web.json_response(response_data, status=status)


async def payment_post(request):
    """
    Функция, обрабатывающая оплату за размещение поста
    """
    data = await request.json()
    order_id = int(data.get('OrderId', None))
    if order_id:
        async for session in get_async_session():
            order = await OrderRepository.get_order(session, order_id)
            post = await PostRepository.get_post(session, order.post_id)
            if order.paid and post.active:
                break
            await OrderRepository.update_order(session, order.id, paid=True)
            chat_id, theme_id = post.channel_id.split('_')
            date_public = datetime.today().date()
            date_expired = date_public + timedelta(days=7)
            main_theme = True if theme_id != 29 else False
            data = {'product_name': post.name,
                    'product_price': post.price,
                    'price_discount': post.discounted_price,
                    'product_marketplace': post.marketplace,
                    'account_url': post.account_url,
                    'discount_proc': post.discount
                    }
            text = await create_text_for_post(data)
            url = await public_post_in_channel(chat_id, post.photo, text, theme_id)
            if main_theme:
                url_main_theme = await public_post_in_channel(chat_id, post.photo,
                                                              text, 29)
            else:
                url_main_theme = url
            await send_message(order.user_telegram, text="Ваше объявление оплачено, размещено в группе на 7 дней",
                               url=url)
            await PostRepository.update_post(session, post.id, active=True,
                                             date_expired=date_expired, date_public=date_public,
                                             url_message=url, method='money', url_message_main=url_main_theme)
            await send_messages_for_admin(session, bot_admin, url, None)

    response_data = {'success': 'OK'}
    return web.json_response(response_data, status=200)


app = web.Application()
app.router.add_get('/check_task/{telegram_id}/{task_id}', check_task)
app.router.add_get('/delete_message/{chat_id}/{id_message}', delete_mes)
app.router.add_get('/count_subscribed', get_count_subscribed)
app.router.add_post('/payment', payment_post)
cors = aiohttp_cors.setup(app
                          , defaults={
            '*': aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers='*',
                    allow_headers='*',
                    allow_methods='*',
            )
    })


async def start_web_server():
    """
    Основная функция для запуска веб сервере
    """
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=8443)
    await site.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(start_web_server())
