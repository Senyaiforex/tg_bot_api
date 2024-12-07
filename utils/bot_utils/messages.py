from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from repository import UserRepository
import logging
from aiogram.exceptions import TelegramNotFound
from contextlib import suppress
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# from aiogram.utils.text_decorations import

async def reply_keyboard():
    menu = [KeyboardButton(text="⬅️ Назад")]
    keyboard = ReplyKeyboardMarkup(keyboard=[
            menu,
    ], resize_keyboard=True, is_persistent=True, one_time_keyboard=False)
    return keyboard


async def delete_message(bot: Bot, user_id: int, previous_id: int):
    """
    Функция для удаления сообщения
    :param bot:
    :param previous_id:
    :return:
    """
    with suppress(*(TelegramBadRequest, TelegramForbiddenError)):
        await bot.delete_message(chat_id=user_id, message_id=previous_id)


async def delete_list_messages(data, bot, user_id):
    list_search = data.get('list_search')
    list_posts = data.get('list_posts')
    if list_search:
        for id_search_message in list_search:
            await delete_message(bot, user_id, id_search_message)
    if list_posts:
        for id_post_message in list_posts:
            await delete_message(bot, user_id, id_post_message)


async def delete_menu(state: FSMContext, bot: Bot, user_id: int) -> None:
    """
    Функция, в которой происходит удаление сообщений меню
    :param state:
    :param bot:
    :param user_id:
    :return:
    """
    data = await state.get_data()
    menu_sel = data.get('menu_sellers')
    menu_buy = data.get('menu_buyers')
    if menu_sel:
        await delete_message(bot, user_id, menu_sel)
    if menu_buy:
        await delete_message(bot, user_id, menu_buy)
    await state.update_data(menu_sellers=None, menu_buyers=None)


async def process_menu_message(picture: FSInputFile,
                               keyboard: InlineKeyboardMarkup | None,
                               bot: Bot,
                               object_interaction: Message | CallbackQuery,
                               state: FSMContext,
                               text: str = None
                               ) -> None:
    """
    Функция для отправки сообщения и удаления предыдущего
    :param data:
    :param bot:
    :param state:
    :return:
    """
    if isinstance(object_interaction, Message):
        user_id = object_interaction.chat.id
        await object_interaction.delete()
    else:
        await object_interaction.answer()
        user_id = object_interaction.from_user.id

    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if previous_message_id:
        await delete_message(bot, user_id, previous_message_id)
    msg = await bot.send_photo(user_id, photo=picture,
                               reply_markup=keyboard,
                               caption=text,
                               parse_mode='Markdown')
    await state.update_data(last_bot_message=msg.message_id)
    await delete_list_messages(data, bot, user_id)


async def message_answer_process(bot: Bot,
                                 object_interaction: Message | CallbackQuery,
                                 state: FSMContext,
                                 text: str | None = None,
                                 keyboard: InlineKeyboardMarkup | None = None,
                                 user: bool = True) -> None:
    """
    Функция для ответа на отправленное сообщение и удаление предыдущего
    :param data:
    :param bot:
    :param state:
    :return:
    """
    if not keyboard and user:
        keyboard = await reply_keyboard()
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message')
    if isinstance(object_interaction, Message):
        with suppress(TelegramBadRequest, TelegramForbiddenError):
            user_id = object_interaction.chat.id
            await object_interaction.delete()
            msg = await object_interaction.answer(text=text,
                                                  reply_markup=keyboard,
                                                  parse_mode='Markdown')
    else:
        await object_interaction.answer()
        user_id = object_interaction.from_user.id
        msg = await object_interaction.message.answer(text=text,
                                                      reply_markup=keyboard,
                                                      parse_mode='Markdown')
    if previous_message_id:
        await delete_message(bot, user_id, previous_message_id)
    await state.update_data(last_bot_message=msg.message_id)
    await delete_list_messages(data, bot, user_id)


async def send_messages_for_admin(session, bot: Bot, url_post: str | None,
                                  username: str | None, text_info: str | None=None) -> None:
    """
    Оповещение всех администраторов
    :param session: Асинхронная сессия
    :param bot: Инстанс бота
    :param url_post: URL опубликованного поста(если есть)
    :param username: Никнейм пользователя(если есть)
    :param text_info: Текст для администраторов
    :return: None
    """
    admins = await UserRepository.get_admins(session)
    for admin in admins:
        with suppress(*(TelegramBadRequest, TelegramForbiddenError)):
            if not text_info and url_post:
                text = f'От автора - @{username}' if username else ''
                text = text.replace("_", "\_")
                text = (f'Здравствуйте, администратор!\n'
                        f'В группе публиковано новое объявление - [перейти]({url_post})\n') + text
            else:
                text = text_info
            await bot.send_message(admin.id_telegram,
                                   text=text,
                                   parse_mode='Markdown')


async def send_message(bot, chat_id, text, keyboard):
    with suppress(*(TelegramBadRequest, TelegramForbiddenError)):
        await bot.send_message(chat_id,
                               text=text,
                               parse_mode='Markdown',
                               reply_markup=keyboard
                               )
