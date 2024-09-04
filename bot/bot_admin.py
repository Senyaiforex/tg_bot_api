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
from database import async_session, Base
from repository import create_user_tg

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
        '🗒Добавить задание': ('Выберите тип задания, которое хотите добавить', select_type_task()),
        '📉Статистика': ('Выберите дальнейшее действие', inline_statistics()),
        '➕Добавить пост': '',
        '🗑Удалить пост': '',
        '🚫Блокировать': '',
        '👥Добавить администратора': '',
        '💰Пул': ('Выберите дальнейшее действие', pull_inline()),
}


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


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
    keyboard = await dict_keyboards[message.text][1]
    user_id = message.from_user.id
    await bot.send_message(chat_id=user_id, text=dict_keyboards[message.text][0], reply_markup=keyboard)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
