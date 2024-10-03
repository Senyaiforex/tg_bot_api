from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from repository import UserRepository
import logging
from aiogram.exceptions import TelegramNotFound

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# from aiogram.utils.text_decorations import

async def reply_keyboard():
    menu = [KeyboardButton(text="Меню")]
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
    try:
        await bot.delete_message(chat_id=user_id, message_id=previous_id)
    except (TelegramBadRequest, TelegramForbiddenError) as ex:
        pass  # логирование в файл


async def delete_list_messages(data, bot, user_id):
    list_search = data.get('list_search')
    list_posts = data.get('list_posts')
    if list_search:
        for id_search_message in list_search:
            await delete_message(bot, user_id, id_search_message)
    if list_posts:
        for id_post_message in list_posts:
            await delete_message(bot, user_id, id_post_message)


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
        try:
            user_id = object_interaction.chat.id
            await object_interaction.delete()
            msg = await object_interaction.answer(text=text,
                                                  reply_markup=keyboard,
                                                  parse_mode='Markdown')
        except TelegramBadRequest as e:
            pass
    else:
        user_id = object_interaction.from_user.id
        msg = await object_interaction.message.answer(text=text,
                                                      reply_markup=keyboard,
                                                      parse_mode='Markdown')
    if previous_message_id:
        await delete_message(bot, user_id, previous_message_id)
    await state.update_data(last_bot_message=msg.message_id)
    await delete_list_messages(data, bot, user_id)


async def send_messages_for_admin(session, bot, url_post, username):
    admins = await UserRepository.get_admins(session)
    text = f'От автора - @{username}' if username else ''
    text = text.replace("_", "\_")
    for admin in admins:
        try:
            await bot.send_message(admin.id_telegram,
                                   text=f'Здравствуйте, администратор!\n'
                                        f'В группе публиковано новое объявление - [перейти]({url_post})\n' + text,
                                   parse_mode='Markdown')
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            pass


async def send_message(bot, chat_id, text, keyboard):
    try:
        await bot.send_message(chat_id,
                               text=text,
                               parse_mode='Markdown',
                               reply_markup=keyboard
                               )
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        pass
