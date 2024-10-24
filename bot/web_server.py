from datetime import datetime, timedelta

from celery.states import state

import aiohttp_cors
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, MessageId
from aiohttp import web
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import back_keyboard, back_menu_user, menu_button
from bot_main import check_task_complete, public_post_in_channel, bot
from loguru import logger
from bot_admin import bot as bot_admin
from database import async_session
from repository import OrderRepository, PostRepository, SellerRepository
from utils.bot_utils.messages import send_messages_for_admin
from utils.bot_utils.util import create_text_for_post

logger.add("logs/web_server/log_file.log",
           retention="5 days",
           rotation='22:00',
           compression="zip",
           level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | "
                  "{level: <8} | "
                  "{name}:{function}:{line} - "
                  "{message}")


async def get_async_session() -> async_session:
    async with async_session() as session:
        yield session
        await session.close()


async def send_message(chat_id, text, url=None, keyboard=None) -> MessageId | None:
    """
    Отправляет сообщение в чат
    """
    keyboard = None if not url else InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Посмотреть', url=url)], menu_button]
    )
    try:
        msg = await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
        return msg.message_id

    except TelegramBadRequest as ex:
        return


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
        count = await bot.get_chat_member_count(chat_id=-1002090610085)
    except TelegramBadRequest as ex:
        logger.error(str(ex), exc_info=True)
        count = 1981
    return web.json_response({'count': count}, status=200)


@logger.catch
async def check_task(request):
    """
    Проверка, что задание выполнено пользователем
    """
    telegram_id = request.match_info.get('telegram_id')
    task_id = request.match_info.get('task_id')
    complete = await check_task_complete(int(telegram_id), int(task_id))
    response_data = {'complete': complete}
    return web.json_response(response_data)


@logger.catch
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


@logger.catch
async def payment_post(request):
    """
    Функция, обрабатывающая оплату за размещение поста
    """
    data = await request.json()
    order_id = int(data.get('OrderId', None))
    logger.info(f"Оплата размещения поста. Заказ - {order_id}")
    if order_id:
        async for session in get_async_session():
            order = await OrderRepository.get_order(session, order_id)
            post = await PostRepository.get_post(session, order.post_id)
            if order.paid and post.active:
                return
            await OrderRepository.update_order(session, order.id, paid=True)
            chat_id, theme_id = post.channel_id.split('_')
            date_public = datetime.today().date()
            date_expired = date_public + timedelta(days=7)
            main_theme = int(theme_id) != 12955
            free_theme = int(theme_id) != 325 and post.discount == 100
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
                                                              text, 12955)
            else:
                url_main_theme = url
            if free_theme:
                url_free_theme = await public_post_in_channel(chat_id, post.photo,
                                                              text, 325)
            else:
                url_free_theme = url
            await send_message(order.user_telegram,
                               text="Ваше объявление оплачено и размещено в группе на 7 дней\n"
                                    "Мы оповестим Вас,"
                                    " как только срок замещения публикации закончится",
                               url=url, keyboard=back_menu_user)
            await PostRepository.update_post(session, post.id, active=True,
                                             date_expired=date_expired, date_public=date_public,
                                             url_message=url, method='money',
                                             url_message_main=url_main_theme,
                                             url_message_free=url_free_theme)
            await SellerRepository.seller_add(session)
            await PostRepository.increment_liquid_posts(session, {'current_money': 1})
            await send_messages_for_admin(session, bot_admin, url, None)
        response_data = {'success': 'OK'}
        return web.json_response(response_data, status=200)
    else:
        response_data = {'error': 'NOT ORDER'}
        return web.json_response(response_data, status=400)


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
