import os
from datetime import datetime, timedelta

from aiohttp.web_exceptions import HTTPException
from celery.states import state

import aiohttp_cors
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, MessageId, \
    LabeledPrice
from aiohttp import web
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from payment import get_url_payment
from keyboards import back_keyboard, back_menu_user, menu_button
from bot_main import check_task_complete, public_post_in_channel, bot, ton_url
from loguru import logger
from bot_admin import bot as bot_admin
from database import async_session
from repository import OrderRepository, PostRepository, SellerRepository, UserRepository
from repository.users import TransactionRepository
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
async def create_link_invoice(request):
    """
    Создать ссылку на оплату звёздами
    """
    data = await request.json()
    amount = int(data.get('amount'))
    user_id = int(data.get('user_id'))
    try:
        prices = [LabeledPrice(label="XTR", amount=amount)]
        link_invoice = await bot.create_invoice_link(
                title="Обмен валюты",
                description=f"Покупка {amount} звёзд",
                prices=prices,
                provider_token="",
                payload=f"pay_stars_{user_id}",
                currency="XTR", )
        response_data = {'success': 'OK', 'link': link_invoice}
        return web.json_response(response_data, status=200)
    except Exception as exception:
        return HTTPException()


@logger.catch
async def create_link_payment(request):
    """
    Создать ссылку на оплату рублями
    """
    data = await request.json()
    amount = int(data.get('amount'))
    user_id = int(data.get('user_id'))
    type_payment = data.get('type_payment')
    count_buy = int(data.get('count_buy'))
    if str(os.getenv('DEBUG')) == 'True':
        response_data = {'success': 'OK', 'link': 'www.testpayment.ru'}
        return web.json_response(response_data, status=200)
    async for session in get_async_session():
        user = await UserRepository.get_user_tg(int(user_id), session)
        if not user.user_name:
            return HTTPException(text="The user does not have a username")
        description = f"buy_stars_{count_buy}" if type_payment == "stars" else f"buy_ton_{count_buy}"
        try:
            order = await OrderRepository.create_order(session, amount,
                                                       int(user_id),
                                                       user.user_name,
                                                       None,
                                                       description)
            description_payment = f"Покупка {count_buy} звёзд" \
                if type_payment == "stars" else f"Покупка {count_buy} TON"
            not_url = os.getenv("EXCHANGE_NOTIFICATION")
            link_payment = await get_url_payment(order.id, amount, description_payment, not_url)
            response_data = {'success': 'OK', 'link': link_payment}
            return web.json_response(response_data, status=200)
        except Exception as exception:
            logger.error(str(exception), exc_info=True)
            return HTTPException(text=str(exception))


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
            await SellerRepository.seller_add(session, date_public)
            await PostRepository.increment_liquid_posts(session, {'current_money': 1})
            await send_messages_for_admin(session, bot_admin, url, None)
        response_data = {'success': 'OK'}
        return web.json_response(response_data, status=200)
    else:
        response_data = {'error': 'NOT ORDER'}
        return web.json_response(response_data, status=400)


@logger.catch
async def payment_currency_exchange(request):
    """
    Функция, обрабатывающая оплату за обмен валюты
    """
    data = await request.json()
    order_id = int(data.get('OrderId', None))
    async for session in get_async_session():
        order = await OrderRepository.get_order(session, order_id)
        description = order.description
        user_id = order.user_telegram
        user_name = order.user_name
        amount = order.amount
        if description.startswith('buy_stars'):
            count_buy = description.split('_')[-1]
            text_admin = (f"*Покупка валюты за {amount} рублей*\n "
                          f"Telegram ID - {user_id}  никнейм - @{user_name}\n\n"
                          f"Тип валюты - *Telegram Stars*\n"
                          f"Количество - *{count_buy}*")
            await send_messages_for_admin(session, bot_admin, None, user_name, text_admin)
            await TransactionRepository.create_transaction(session, user_id, 'money', amount,
                                                           'stars', count_buy)
        elif description.startswith("buy_ton"):
            count_buy = description.split('_')[-1]
            text_admin = (f"*Покупка валюты за {amount} рублей*\n "
                          f"Telegram ID - {user_id}  никнейм - @{user_name}\n\n"
                          f"Тип валюты - *TON*\n"
                          f"Количество - *{count_buy}*")
            await send_messages_for_admin(session, bot_admin, None, user_name, text_admin)
            await TransactionRepository.create_transaction(session, user_id, 'money', amount,
                                                           'ton', count_buy)
        user = await UserRepository.get_user_tg(user_id, session)
        await user.update_count_coins(session, 1000, "Бонус за покупку валюты")
    response_data = {'success': 'OK'}
    return web.json_response(response_data, status=200)


@logger.catch
async def send_admins_by_transactions(request):
    """
    Оповестить администраторов о совершённой транзакции
    """
    data = await request.json()
    text = data.get('text')
    username = data.get('username')
    async for session in get_async_session():
        await send_messages_for_admin(session, bot_admin, None, username, text)
    response_data = {'success': 'OK'}
    return web.json_response(response_data, status=200)


app = web.Application()
app.router.add_get('/check_task/{telegram_id}/{task_id}', check_task)
app.router.add_get('/delete_message/{chat_id}/{id_message}', delete_mes)
app.router.add_get('/count_subscribed', get_count_subscribed)
app.router.add_post('/create_link_invoice', create_link_invoice)
app.router.add_post('/payment', payment_post)
app.router.add_post('/create_link_payment', create_link_payment)
app.router.add_post('/currency-payment', payment_currency_exchange)
app.router.add_post('/send_admins', send_admins_by_transactions)

cors = aiohttp_cors.setup(app
                          , defaults={
            '*': aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    allow_methods='*',
                    allow_headers='*',
                    expose_headers='*',
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
