import os
import uuid
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, CallbackQuery, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from requests import session
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards import *
import functools
from database import async_session
from repository import create_user_tg, create_task, create_user_admin, get_user_tg, get_pull, set_pull_by_size
from utils import get_info_users
from utils.bot_utils.text_static import *
from utils.bot_utils.utills_db import get_info_from_user, get_all_transactions, get_friends, get_friends_by_user, \
    block_user_by_username


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


superuser_ids = [718586333, 98723123312, 5321413149]
admin_ids = [718586333, 987654321, 5321413149]
MEDIA_DIR = 'media'
BOT_TOKEN = "7279689856:AAGp9CToYaxJYWZdCL8YG7nxZ1orddKWdlQ"

dict_keyboards = {
        '🗒Добавить задание': ('Выберите тип задания, которое хотите добавить', select_type_task),
        '📉Статистика': ('Выберите дальнейшее действие', inline_statistics),
        '➕Добавить пост': '',
        '🗑Удалить пост': '',
}


class States(StatesGroup):
    wait_descript = State()
    wait_url = State()
    confirmation = State()
    wait_telegram_admin = State()
    wait_username = State()
    wait_telegram_block = State()
    wait_type = State()
    wait_pull = State()


class StatesInfo(StatesGroup):
    wait_username = State()
    wait_username_block = State()


bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def permissions_check(func):
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        async for session in get_async_session():
            user = await get_user_tg(user_id, session)
            if not user or all((user.admin == False, user.superuser == False)):
                await message.answer(message_no_access)
                return
            return await func(message, session, *args, **kwargs)

    return wrapper


@dp.message(Command("start"))
@permissions_check
async def start(message: Message, session) -> None:
    """
    Функция обработки команды /start, для начала работы с ботом
    :param message: сообщение боту
    :param command: команда /start
    :return:
    """
    picture = FSInputFile('static/start_pic.jpg')
    user_id = message.from_user.id
    if user_id not in admin_ids and user_id not in superuser_ids:
        await bot.send_photo(user_id, caption=message_no_access,
                             photo=picture)
        return
    superuser = user_id in superuser_ids
    caption = message_for_admin + message_superuser if superuser else message_for_admin
    keyboard = await menu_admin(superuser)
    await bot.send_photo(chat_id=user_id, photo=picture,
                         caption=caption,
                         reply_markup=keyboard, parse_mode='Markdown')


@dp.message(F.text.in_(dict_keyboards))
@permissions_check
async def inline_buttons_menu(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопки меню
    :param message:
    :param state:
    :return:

    """
    await state.set_state(None)
    message_id = message.message_id
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
        except Exception as e:pass
    text, func = dict_keyboards[message.text]
    keyboard = await func()
    user_id = message.from_user.id
    msg = await bot.send_message(chat_id=user_id, text=dict_keyboards[message.text][0], reply_markup=keyboard)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(F.text == '👥Добавить администратора')
@permissions_check
async def inline_buttons_menu(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку добавить администратора
    :param message:
    :param state:
    :return:

    """
    await state.set_state(None)
    message_id = message.message_id
    user_id = message.from_user.id
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
        except Exception as e:
            pass
    msg = await bot.send_message(chat_id=user_id,
                                 text='Введите telegram_id пользователя, '
                                      'которого хотите добавить в администраторы',
                                 )
    await state.set_state(States.wait_telegram_admin)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(States.wait_telegram_admin)
@permissions_check
async def add_telegram_admin(message: Message, session, state: FSMContext) -> None:
    """
    :param message:
    :param state:
    :return:

    """
    message_id = message.message_id
    user_id = message.from_user.id
    text = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)

    if not text.isdigit():
        msg = await bot.send_message(chat_id=user_id,
                                     text='telegram_id должен состоять только из цифр, попробуйте ещё раз',
                                     )
        await state.set_state(None)
    else:
        msg = await bot.send_message(chat_id=user_id,
                                     text='Введите username пользователя, которого хотите добавить в администраторы',
                                     )
        await state.set_state(States.wait_username)
        await state.update_data(telegram_admin=text)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(States.wait_username)
@permissions_check
async def add_username_admin(message: Message, session, state: FSMContext) -> None:
    """
    :param message:
    :param state:
    :return:

    """
    message_id = message.message_id
    text = message.text
    data = await state.get_data()
    telegram_admin = data.get('telegram_admin')
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    msg = await message.answer(text=f'Пользователь @{text} добавлен в администраторы')
    await asyncio.sleep(2)
    await msg.delete()
    await create_user_admin(int(telegram_admin), text, session)


@dp.callback_query(lambda c: c.data.startswith('task'))
async def add_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
    type_task = callback_query.data.split('_')[1]
    msg = await callback_query.message.answer(text='Введите описание задания:')
    await state.set_state(States.wait_descript)
    await state.update_data(last_bot_message=msg.message_id)
    await state.update_data(type_task=type_task)


@dp.message(States.wait_descript)
async def wait_url(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    description = message.text
    previous_message_id = data.get('last_bot_message')
    user_id = message.from_user.id
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    msg = await message.answer(text='Отправьте ссылку на задание в виде\n '
                                    'https://example/product/one.com')
    await message.delete()
    await state.set_state(States.wait_url)
    await state.update_data(last_bot_message=msg.message_id)
    await state.update_data(description=description)


@dp.message(States.wait_url)
@permissions_check
async def wait_url(message: Message, session, state: FSMContext) -> None:
    data = await state.get_data()
    url = message.text
    previous_message_id = data.get('last_bot_message')
    user_id = message.from_user.id
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    if 'http' not in url:
        msg = await message.answer(text='Пожалуйста, отправьте '
                                        'ссылку на задание в следующем формате:\n'
                                        'https://example/product/one.com')
        await state.update_data(last_bot_message=msg.message_id)
        return
    await message.delete()
    msg = await message.answer(text='Задание успешно добавлено!')
    await asyncio.sleep(2)
    await msg.delete()
    type_task, description = data.get('type_task'), data.get('description')
    await create_task(url, description, type_task, session)
    await state.clear()


@dp.callback_query(lambda c: c.data.startswith('all_info_users'))
async def statistic_users(callback_query: CallbackQuery, state: FSMContext) -> None:
    async for session in get_async_session():
        dict_info = await get_info_users(session)
    text = ''
    for msg, value in dict_info.items():
        text += f'{msg} - {value}\n'
    await callback_query.message.edit_text(text=text)


@dp.callback_query(lambda c: c.data.startswith('info_user'))
async def info_user(callback_query: CallbackQuery, state: FSMContext) -> None:
    msg = await callback_query.message.answer(
            text='Введите никнейм пользователя, '
                 'о котором хотите узнать информацию')
    await state.set_state(StatesInfo.wait_username)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(StatesInfo.wait_username)
async def username_info(message: Message, state: FSMContext) -> None:
    username = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    user_id = message.from_user.id
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    async for session in get_async_session():
        dict_info = await get_info_from_user(username, session)
        if not dict_info:
            msg = await message.answer(text='Пользователь с таким никнеймом не найден')
            await message.delete()
            await state.update_data(last_bot_message=msg.message_id)
            return
    text = ''
    for msg, value in dict_info.items():
        text += f'{msg} - {value}\n'
    msg = await message.answer(text=text,
                               reply_markup=await user_info_keyboard(dict_info['Телеграм id пользователя']))
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)


@dp.callback_query(lambda c: c.data.startswith('transactions'))
async def info_user(callback_query: CallbackQuery, state: FSMContext) -> None:
    telegram_id = int(callback_query.data.split('_')[1])
    data = await state.get_data()
    user_id = callback_query.message.chat.id
    async for session in get_async_session():
        transactions = await get_all_transactions(telegram_id, session)
        if not transactions:
            await callback_query.message.edit_text('У данного пользователя отсутствуют транзакции')
            return
    text = ''
    for value in transactions:
        text += f'Дата: {value["Дата"]}, Сумма: {value["Сумма"]}, Тип транзакции: {value["Описание"]}\n'
    msg = await callback_query.message.answer(text=text)
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    await state.update_data(last_bot_message=msg.message_id)


@dp.callback_query(lambda c: c.data.startswith('friends'))
async def info_user(callback_query: CallbackQuery, state: FSMContext) -> None:
    telegram_id = int(callback_query.data.split('_')[1])
    data = await state.get_data()
    user_id = callback_query.message.chat.id
    async for session in get_async_session():
        friends = await get_friends_by_user(telegram_id, session)
        if not friends:
            await callback_query.message.edit_text('У данного пользователя отсутствуют транзакции')
            return
    text = ''
    for value in friends:
        text += (f'Никнейм: @{value["username"]}, Количество монет: {value["count_coins"]}, '
                 f'Уровень: {value["level"]}, Дата регистрации: {value["date_registration"]}\n')
    msg = await callback_query.message.answer(text=text)
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(F.text == '🚫Блокировать')
@permissions_check
async def block_user(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 🚫Блокировать
    :param message:
    :param state:
    :return:

    """
    await state.set_state(None)
    message_id = message.message_id
    user_id = message.from_user.id
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    msg = await bot.send_message(chat_id=user_id,
                                 text='Введите никнейм пользователя, '
                                      'которого хотите заблокировать',
                                 )
    await state.set_state(StatesInfo.wait_username_block)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(StatesInfo.wait_username_block)
async def block_user_by_name(message: Message, state: FSMContext) -> None:
    username = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    user_id = message.from_user.id
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    await message.delete()
    async for session in get_async_session():
        block = await block_user_by_username(username, session)
        if not block:
            msg = await message.answer(text='Пользователь с таким никнеймом не найден')
            await state.update_data(last_bot_message=msg.message_id)
            return
    msg = await message.answer(text=f'Пользоваеть @{username} заблокирован!')
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(F.text == '💰Пул')
@permissions_check
async def block_user(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 🚫Блокировать
    :param message:
    :param state:
    :return:

    """
    await state.set_state(None)
    message_id = message.message_id
    user_id = message.from_user.id
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    pull = await get_pull(session)
    msg = await message.answer(
            text=f'Ваш текущий пулл: - {pull.pull_size}. Оставшееся количество - 4 821 500',
            reply_markup=await pull_keyboard()
    )
    await state.set_state(StatesInfo.wait_username_block)
    await state.update_data(last_bot_message=msg.message_id)


@dp.callback_query(lambda c: c.data == 'set_pull')
async def set_pull(callback_query: CallbackQuery, state: FSMContext) -> None:
    msg = await callback_query.message.answer(
            text='Введите количество пула')
    await state.set_state(States.wait_pull)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(States.wait_pull)
async def wait_url(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    size = message.text
    previous_message_id = data.get('last_bot_message')
    user_id = message.from_user.id
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    await message.delete()
    if not size.isdigit():
        msg = await message.answer(
                text=f'Пожалуйста, введите правильный пулл, он должен состоять только из цифр!'
        )
        await state.update_data(last_bot_message=msg.message_id)
        return
    async for session in get_async_session():
        await set_pull_by_size(int(size), session)
    msg = await message.answer(
            text=f'Установлен новый пулл. Размер - {size}'
    )
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
