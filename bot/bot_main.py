import multiprocessing
import os
import uuid
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, CallbackQuery, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from utils.bot_utils import *
import functools
from keyboards import *
from database import async_session
from repository import create_user_tg
from repository import get_user_by_telegram_id, get_task_by_id, add_task
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MEDIA_DIR = 'media'


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


os.makedirs(MEDIA_DIR, exist_ok=True)
BOT_TOKEN = "7006667556:AAFzRm7LXS3VoyqCIvN5QJ-8RRsixZ9uPek"
API_TOKEN = 'YOUR_BOT_API_TOKEN'
CHANNEL_ID = '@Buyer_Marketplace'
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
web_app_url = 'https://tg-botttt.netlify.app'


async def is_user_subscribed(user_id: int, channel_id: str) -> bool:
    start_time = time.time()
    member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    logger.info(f'{start_time - time.time()}')
    return member.status in ["member", "administrator", "creator"]


def subscribed(func):
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        if not await is_user_subscribed(user_id, CHANNEL_ID):
            await message.answer("Чтобы пользоваться ботом, необходимо подписаться на канал: @Buyer_Marketplace\n"
                                 "После подписки на канал Вы можете снова использовать бот, нажимая на любые кнопки в меню.")
            return
        return await func(message, *args, **kwargs)

    return wrapper


class PostStates(StatesGroup):
    wait_name = State()
    wait_photo = State()
    wait_price = State()
    wait_discount = State()
    wait_marketplace = State()
    wait_url_account = State()
    wait_channel = State()
    wait_product_search = State()


@dp.message(Command("start"))
async def start(message: Message, command: CommandObject) -> None:
    """
    Функция обработки команды /start, для начала работы с ботом
    :param message: сообщение боту
    :param command: команда /start
    :return:
    """
    picture = FSInputFile('static/start_pic.jpg')
    user_id = message.from_user.id
    username = message.from_user.username
    inviter_id = None
    args = command.args
    if args and args.startswith("invited_by_"):
        inviter_id = int(args.split("_")[2])
    if await is_user_subscribed(user_id, CHANNEL_ID):
        # Если пользователь подписан, показываем меню
        text = "Добро пожаловать!\n"
        keyboard_reply = await start_reply_keyboard()
        await bot.send_photo(user_id, caption=text, photo=picture, parse_mode='Markdown',
                             reply_markup=keyboard_reply)
    else:
        # Если пользователь не подписан, показываем сообщение с просьбой подписаться
        text = ("Добро пожаловать!\n"
                "Чтобы пользоваться данным ботом необходимо подписаться на канал: @Buyer_Marketplace\n"
                "После подписки снова нажмите /start")
        keyboard = await start_keyboard()
        await bot.send_photo(chat_id=user_id, photo=picture, caption=text, reply_markup=keyboard)
    async for session in get_async_session():
        if await get_user_bot(user_id, session):
            return  # Если пользователь уже есть в базе, выходим из функции
        if inviter_id:
            await handle_invitation(inviter_id, user_id, username, session)
        else:
            await create_user_tg(user_id, username, session)


@dp.message(Command("web"))
@subscribed
async def webapp(message: Message, command: CommandObject, state: FSMContext) -> None:
    """
    Функция обработки команды для перехода в веб приложение
    :param message:
    :param command:
    :return:
    """
    user_id = message.from_user.id
    web_button = KeyboardButton(text="Запустить", web_app=WebAppInfo(url=web_app_url))
    # Создаем клавиатуру с кнопкой
    keyboard = ReplyKeyboardMarkup(keyboard=[[web_button]], resize_keyboard=True)
    # Отправляем сообщение с клавиатурой
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    msg = await message.answer("Нажмите 'Запустить', чтобы открыть веб-приложение:", reply_markup=keyboard)
    await state.update_data(last_bot_message=msg.message_id)
    await message.delete()


@dp.message(F.text == 'Меню')
@subscribed
async def menu(message: Message, state: FSMContext) -> None:
    """
    Функция отображения меню
    :param message:
    :return:
    """
    picture = FSInputFile('static/menu_pic.jpg')
    user_id = message.from_user.id
    keyboard = await menu_keyboard()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    msg = await bot.send_photo(user_id, photo=picture, reply_markup=keyboard)
    await state.update_data(last_bot_message=msg.message_id)
    await message.delete()


@dp.message(F.text == 'Опубликовать пост')
@subscribed
async def public(message: Message, state: FSMContext) -> None:
    """
    Функция обработки команды для размещения поста
    :param message:
    :return:
    """
    text = ("По вопросам условий размещения "
            "объявлений и иным вариантам сотрудничества "
            "просьба обращаться к менеджерам с помощью кнопки 'Написать менеджеру'")
    picture = FSInputFile('static/public_pic.jpg')
    user_id = message.from_user.id
    keyboard = await public_keyboard()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    msg = await bot.send_photo(user_id, photo=picture, reply_markup=keyboard)
    await state.update_data(last_bot_message=msg.message_id)
    await message.delete()


@dp.message(F.text == 'Каталог')
@subscribed
async def catalog(message: Message, state: FSMContext) -> None:
    """
    Функция отображения каталога товаров
    :param message:
    :return:
    """
    picture = FSInputFile('static/catalog_pic.jpg')
    user_id = message.from_user.id
    keyboard = await catalog_keyboard()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    msg = await bot.send_photo(user_id, photo=picture, reply_markup=keyboard)
    await state.update_data(last_bot_message=msg.message_id)
    await message.delete()


@dp.callback_query(lambda c: c.data == 'back_to_menu')
async def back_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопки возврата в меню
    :param callback_query:
    :return:
    """
    user_id = callback_query.from_user.id
    picture = FSInputFile('static/menu_pic.jpg')
    keyboard = await menu_keyboard()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
    msg = await bot.send_photo(user_id, photo=picture, reply_markup=keyboard)
    await state.update_data(last_bot_message=msg.message_id)

    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'public')
async def add_post_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопки возврата в меню
    :param callback_query:
    :return:
    """
    text = ("По вопросам условий размещения "
            "объявлений и иным вариантам сотрудничества "
            "просьба обращаться к менеджерам с помощью кнопки 'Написать менеджеру'")
    user_id = callback_query.from_user.id
    picture = FSInputFile('static/public_pic.jpg')
    keyboard = await public_keyboard()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
    msg = await bot.send_photo(user_id, photo=picture, reply_markup=keyboard, caption=text)
    await state.update_data(last_bot_message=msg.message_id)

    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'catalog')
async def catalog_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопки возврата в меню
    :param callback_query:
    :return:
    """
    text = ("По вопросам условий размещения "
            "объявлений и иным вариантам сотрудничества "
            "просьба обращаться к менеджерам с помощью кнопки 'Написать менеджеру'")
    user_id = callback_query.from_user.id
    picture = FSInputFile('static/catalog_pic.jpg')
    keyboard = await catalog_keyboard()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
    msg = await bot.send_photo(user_id, photo=picture, reply_markup=keyboard, caption=text)
    await state.update_data(last_bot_message=msg.message_id)

    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'search')
async def catalog_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопки поиска товара
    :param callback_query:
    :return:
    """
    user_id = callback_query.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
    msg = await bot.send_message(user_id, text="Тут вы можете добавить нужный вам товар, когда он появится в продаже "
                                               "со скидкой, мы отправим вам сообщение в телеграмм!\nПример: Юбка")
    await state.update_data(last_bot_message=msg.message_id)
    await state.set_state(PostStates.wait_product_search)
    await callback_query.answer()


@dp.message(PostStates.wait_product_search)
async def process_product_name(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.update_data(product_seach=message.text)
    msg = await message.answer(f"✅ Отлично, добавили подписку на {message.text}\n"
                               "Когда опубликуется, вам придет уведомление.")
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)


@dp.callback_query(lambda c: c.data.startswith('add_post'))
async def add_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = callback_query.data
    user_id = callback_query.from_user.id
    method = data.split('_')[2]
    if method == 'free':
        data = await state.get_data()
        previous_message_id = data.get('last_bot_message')
        if previous_message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
        msg = await bot.send_message(user_id, text='Введите название товара:')
        await state.set_state(PostStates.wait_name)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(PostStates.wait_name)
async def process_product_name(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.update_data(product_name=message.text)
    msg = await message.answer("Название товара успешно сохранено! "
                               "Теперь загрузите фото товара.")
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    await state.set_state(PostStates.wait_photo)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(PostStates.wait_photo, F.content_type == 'photo')
async def process_product_photo(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    photo = message.photo[-1]  # Выбираем фото с наибольшим разрешением
    file_id = photo.file_id
    file_info = await bot.get_file(file_id)
    file_extension = file_info.file_path.split('.')[-1]  # Определяем расширение файла
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"  # Создаем уникальное имя файла
    file_path = os.path.join(MEDIA_DIR, unique_filename)
    # Скачиваем файл
    await bot.download_file(file_info.file_path, file_path)
    # Сохраняем только имя файла в состоянии
    await state.update_data(product_photo=unique_filename)
    user_data = await state.get_data()
    product_name = user_data.get('product_name')
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)

    msg = await message.answer(f"Фото товара '{product_name}' успешно сохранено! "
                               f"Теперь укажите стоимость товара на маркетплейсе в данный момент")
    await state.set_state(PostStates.wait_price)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(PostStates.wait_photo)
async def process_invalid_photo(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    msg = await message.answer("Пожалуйста, отправьте фотографию товара.")
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(PostStates.wait_price)
async def process_product_price(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    if not message.text.isdigit():
        msg = await message.answer("Цена должна быть числом. Попробуйте ещё раз.")
        await state.update_data(last_bot_message=msg.message_id)
        return
    await state.update_data(product_price=message.text)
    # Подтверждение публикации
    msg = await message.answer("Укажите стоимость товара со скидкой(Кэшбеком).\n"
                               "Обратите внимание, что скидка должна быть"
                               "реальная и отличаться от стоимости "
                               "на маркетплейсе минимум на 15%")
    await state.set_state(PostStates.wait_discount)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(PostStates.wait_discount)
async def process_product_discount(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    if not message.text.isdigit():
        msg = await message.answer("Скидка(Кэшбек) должна быть числом. Попробуйте ещё раз.")
        await state.update_data(last_bot_message=msg.message_id)
        return
    await state.update_data(product_discount=message.text)
    # Подтверждение публикации
    msg = await message.answer("Выберите, на каком маркетплейсе будет покупка, "
                               "либо нажмите на кнопку 'Пропустить'",
                               reply_markup=await marketpalce_choice()
                               )
    await state.set_state(PostStates.wait_marketplace)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(F.text.in_({'WB', 'OZON', 'Пропустить'}), PostStates.wait_marketplace)
async def marketplace(message: Message, state: FSMContext) -> None:
    # Обрабатываем текст, который был отправлен пользователем
    text = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    if text == 'Пропустить':
        text = ' '
    await state.update_data(product_marketplace=text)
    msg = await message.answer("Укажите ссылку на аккаунт, которому будут"
                               "писать покупатели, переходящие по "
                               "кнопке 'узнать условия'"
                               )
    await state.set_state(PostStates.wait_url_account)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(PostStates.wait_url_account)
async def account_url(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    await state.update_data(account_url=message.text)
    # Подтверждение публикации
    msg = await bot.send_message(user_id, "❗️Выберите необходимый канал для публикации",
                                 reply_markup=await channel_choice()
                                 )
    await state.set_state(PostStates.wait_channel)
    await state.update_data(last_bot_message=msg.message_id)


@dp.callback_query(lambda c: c.data == 'buyer', PostStates.wait_channel)
async def choice_group(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = callback_query.data
    user_id = callback_query.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.edit_message_text(chat_id=user_id, message_id=previous_message_id,
                                    text=f'💢 Выбрана публикация на канал {callback_query.message.text}')
    await state.update_data(channel=callback_query.message.text)
    user_data = await state.get_data()
    # Получаем данные
    product_name = user_data.get('product_name')
    product_price = user_data.get('product_price')
    product_discount = user_data.get('product_discount')
    product_photo_path = user_data.get('product_photo')
    product_marketplace = user_data.get('product_marketplace')
    url_product = user_data.get('account_url')
    channel = callback_query.message.text
    proc = (int(product_discount) / int(product_price)) * 100
    caption = (f"Ваше объявление:\n"
               f"Кэшбек: {product_discount} р. ({int(proc)}%)\n"
               f"Цена: {product_price} р.\n"
               f"Цена для вас: {int(product_price) - int(product_discount)} р.\n"
               f"Товар: {product_name}")
    caption = caption + f"\nМаркетплейс - {product_marketplace}" \
        if product_marketplace != 'Пропустить' else caption
    file_path = os.path.join(os.getcwd(), MEDIA_DIR, product_photo_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл по пути {file_path} не найден")
    await bot.send_photo(chat_id=user_id, photo=FSInputFile(file_path),
                         caption=caption)
    msg = await bot.send_message(user_id, text="🌟Объявление готово для публикации!\n\n"
                                               "Обязательно проверьте правильность заполненных полей и ссылок!\n\n"
                                               "Для окончания публикации нажмите кнопку ниже!",
                                 reply_markup=await finish_public())
    await state.update_data(last_bot_message=msg.message_id)


@dp.callback_query(lambda c: c.data == 'finish_public', PostStates.wait_channel)
async def finish(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопки опубликовать
    :param callback_query:
    :return:
    """
    user_id = callback_query.from_user.id
    user_data = await state.get_data()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)

    msg = await bot.send_message(user_id, text='Успешно! Ваше объявление опубликовано!')
    await state.update_data(last_bot_message=msg.message_id)
    await state.clear()


async def get_channel_id_by_url(url: str) -> str:
    channel_id = url.split("//")[-1].split("/")[1]
    return f'@{channel_id}'


async def check_task_complete(telegram_id: int, task_id: int) -> bool:
    async for session in get_async_session():
        user = await get_user_by_telegram_id(telegram_id, session)
        task = await get_task_by_id(task_id, session)
        if task.type_task == 'subscribe':
            if await is_user_subscribed(telegram_id, await get_channel_id_by_url(task.url)):
                await add_task(user, task, session)
                return True
        return False


async def main():
    subprocess.Popen(["python", "web_server.py"])
    await asyncio.sleep(2)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
