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
from keyboards import *
import functools
from database import async_session
from repository import create_user_tg, create_task


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


superuser_ids = [718586333, 98723123312]
admin_ids = [718586333, 987654321]
MEDIA_DIR = 'media'
BOT_TOKEN = "7279689856:AAGp9CToYaxJYWZdCL8YG7nxZ1orddKWdlQ"
CHANNEL_ID = '@Buyer_Marketplace'
message_for_admin = ("Здравствуйте, администратор!\n"
                     "В этом боте Вам доступны следующие функции:\n"
                     "🗒Добавить задание - Добавить новое задание\n"
                     "📉Статистика - Показать статистику\n"
                     "➕Добавить пост - Добавить новый пост\n"
                     "🗑Удалить пост - Удалить пост\n"
                     "🚫Блокировать - Заблокировать пользователя\n"
                     )
message_superuser = ("👥Добавить администратора - Добавить нового администратора\n"
                     "💰Пул - Задать пул для приложения")
message_no_access = ("Здравствуйте! У вас недостаточно прав для использования данного бота. \n"
                     f"Используйте бот {CHANNEL_ID}")

dict_keyboards = {
        '🗒Добавить задание': ('Выберите тип задания, которое хотите добавить', select_type_task),
        '📉Статистика': ('Выберите дальнейшее действие', inline_statistics),
        '➕Добавить пост': '',
        '🗑Удалить пост': '',
        '🚫Блокировать': '',
        '👥Добавить администратора': '',
        '💰Пул': ('Выберите дальнейшее действие', pull_inline),
}


class TaskStates(StatesGroup):
    wait_descript = State()
    wait_url = State()
    confirmation = State()

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def permissions_check(func):
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        if user_id not in admin_ids and user_id not in superuser_ids:
            await message.answer(message_no_access)
            return
        return await func(message, *args, **kwargs)

    return wrapper


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
async def inline_buttons_menu(message: Message, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопки меню
    :param message:
    :param state:
    :return:

    """
    message_id = message.message_id
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    text, func = dict_keyboards[message.text]
    keyboard = await func()
    user_id = message.from_user.id
    msg = await bot.send_message(chat_id=user_id, text=dict_keyboards[message.text][0], reply_markup=keyboard)
    await state.update_data(last_bot_message=msg.message_id)


@dp.callback_query(lambda c: c.data.startswith('task'))
async def add_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
    data = callback_query.data
    user_id = callback_query.from_user.id
    type_task = data.split('_')[1]
    msg = await bot.send_message(chat_id=user_id, text='Введите описание задания:')
    await state.set_state(TaskStates.wait_url)
    await state.update_data(last_bot_message=msg.message_id)
    await state.update_data(type_task=type_task)


@dp.message(TaskStates.wait_url)
async def wait_url(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    description = message.text
    previous_message_id = data.get('last_bot_message')
    user_id = message.from_user.id
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    msg = await bot.send_message(chat_id=user_id, text='Отправьте ссылку на задание в виде\n '
                                                       'https://example/product/one.com')
    await state.set_state(TaskStates.confirmation)
    await state.update_data(last_bot_message=msg.message_id)
    await state.update_data(description=description)


@dp.message(TaskStates.confirmation)
async def wait_url(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    url = message.text
    previous_message_id = data.get('last_bot_message')
    user_id = message.from_user.id
    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)
    if 'http' not in url:
        msg = await bot.send_message(chat_id=user_id, text='Пожалуйста, отправьте '
                                                           'ссылку на задание в следующем формате:\n'
                                                           'https://example/product/one.com')
        await state.update_data(last_bot_message=msg.message_id)
        return
    msg = await bot.send_message(chat_id=user_id, text='Задание успешно добавлено!')
    await state.set_state(TaskStates.wait_url)
    await state.update_data(last_bot_message=msg.message_id)
    await state.update_data(url=url)
    data_new = await state.get_data()
    async for session in get_async_session():
        await create_task(data_new.get('url'), data_new.get('description'),
                          data_new.get('type_task'), session)
    await state.clear()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
