import re
import asyncio
import emoji
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, CallbackQuery, Chat
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import functools
from bot_admin import bot as bot_admin
from payment import get_url_payment
from keyboards import *
from database import async_session
from repository import *
import subprocess
from loguru import logger
from states import PostStates, DeletePost
from utils.bot_utils.messages import process_menu_message, message_answer_process, delete_message, reply_keyboard, \
    send_messages_for_admin
from utils.bot_utils.util import *

MEDIA_DIR = 'media'
MAX_SIZE_FILE = int(1.5 * 1024 * 1024)

logger.add("logs/logs_bot/log_file.log",
           retention="5 days",
           rotation='19:00',
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


os.makedirs(MEDIA_DIR, exist_ok=True)
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv("CHANNEL_ID")
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def is_user_subscribed(user_id: int, channel_id: str) -> bool:
    """
    Функция проверки, что пользователь с user_id подписан на канал channel_id
    """
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest as e:
        return False


def subscribed(func):
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        if not await is_user_subscribed(user_id, CHANNEL_ID):
            await message.answer(txt_us.no_subscribe)
            return
        async for session in get_async_session():
            user = await UserRepository.get_user_tg(user_id, session)
            if user and user.active == False:
                await message.answer(txt_us.block)
                return
            elif not user:
                await UserRepository.create_user_tg(user_id, message.from_user.username, session)
        return await func(message, *args, **kwargs)

    return wrapper


def subscribed_call(func):
    @functools.wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        if not await is_user_subscribed(user_id, CHANNEL_ID):
            await callback.message.answer(txt_us.no_subscribe)
            return
        async for session in get_async_session():
            user = await UserRepository.get_user_tg(user_id, session)
            if user and user.active == False:
                await callback.message.answer(txt_us.block)
                return
            elif not user:
                await UserRepository.create_user_tg(user_id, callback.from_user.username, session)
        return await func(callback, *args, **kwargs)

    return wrapper


@dp.message(Command("start"))
@logger.catch
async def start(message: Message, command: CommandObject, state: FSMContext) -> None:
    """
    Функция обработки команды /start, для начала работы с ботом
    """
    picture = FSInputFile('static/menu_pic.jpg')
    user_id = message.from_user.id
    username = message.from_user.username
    inviter_id = None
    args = command.args
    if args and args.startswith("invited_by_"):
        inviter_id = int(args.split("_")[2])
    elif args and args.startswith("products_search"):
        await message_answer_process(bot, message,
                                     state, txt_us.info_search, keyboard=await search_keyboard())
        return
    if await is_user_subscribed(user_id, CHANNEL_ID):
        # Если пользователь подписан, показываем меню
        keyboard_reply = await menu_keyboard()
        await bot.send_photo(user_id, photo=picture, parse_mode='Markdown',
                             reply_markup=keyboard_reply)
    else:
        keyboard = await start_keyboard()
        await bot.send_photo(chat_id=user_id, photo=picture,
                             caption=txt_us.no_subscribe, reply_markup=keyboard)
    async for session in get_async_session():
        if await get_user_bot(user_id, session):
            return  # Если пользователь уже есть в базе, выходим из функции
        if inviter_id:
            await handle_invitation(inviter_id, user_id, username, session)
        else:
            await UserRepository.create_user_tg(user_id, username, session)


@dp.message(F.text == "⬅️ Назад")
@subscribed
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    picture = FSInputFile('static/menu_pic.jpg')
    keyboard = await menu_keyboard()
    await process_menu_message(picture, keyboard, bot, message, state)


@dp.message(F.text == '⬅️ Назад')
@subscribed
async def menu(message: Message, state: FSMContext) -> None:
    """
    Функция обработки нажатия на кнопку «Меню»
    """
    await state.set_state(None)
    picture = FSInputFile('static/menu_pic.jpg')
    keyboard = await menu_keyboard()
    await process_menu_message(picture, keyboard, bot, message, state)


# @dp.message(F.text == 'Опубликовать пост')
# @subscribed
# async def public(message: Message, state: FSMContext) -> None:
#     """
#     Функция обработки нажатия на кнопку «Опубликовать пост»
#     """
#     await state.set_state(None)
#     picture = FSInputFile('static/public_pic.jpg')
#     keyboard = await public_keyboard()
#     await process_menu_message(picture, keyboard, bot, message, state)
#
#
# @dp.message(F.text == 'Каталог')
# @subscribed
# async def catalog(message: Message, state: FSMContext) -> None:
#     """
#     Функция обработки нажатия на кнопку «Каталог»
#     """
#     await state.set_state(None)
#     picture = FSInputFile('static/catalog_pic.jpg')
#     keyboard = await catalog_keyboard()
#     await process_menu_message(picture, keyboard, bot, message, state)


@dp.callback_query(lambda c: c.data == 'back_to_menu')
@subscribed_call
async def back_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «В меню»
    """
    await state.set_state(None)
    picture = FSInputFile('static/menu_pic.jpg')
    keyboard = await menu_keyboard()
    await process_menu_message(picture, keyboard, bot, callback_query, state)


@dp.callback_query(lambda c: c.data == 'public')
@subscribed_call
async def add_post_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать пост»
    """
    picture = FSInputFile('static/public_pic.jpg')
    keyboard = await public_keyboard()
    await process_menu_message(picture, keyboard, bot,
                               callback_query, state,
                               txt_us.cooperation)


@dp.callback_query(lambda c: c.data == 'delete_post_by_name')
async def add_post_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать пост»
    """
    await message_answer_process(bot, callback_query,
                                 state, "Отправьте ссылку на сообщение в группе с упоминанием вашего никнейма\n"
                                        "Если такое сообщение есть, то мы удалим его")
    await state.set_state(DeletePost.wait_url_post)


@dp.callback_query(lambda c: c.data == 'catalog')
@subscribed_call
async def catalog_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Каталог товаров»
    """
    picture = FSInputFile('static/catalog_pic.jpg')
    keyboard = await catalog_keyboard()
    await process_menu_message(picture, keyboard, bot,
                               callback_query, state,
                               txt_us.cooperation)


@dp.callback_query(lambda c: c.data == 'search')
@subscribed_call
async def search_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «➕Добавить товар в лист ожидания»
    """
    async for session in get_async_session():
        search_list = await SearchListRepository.get_search_by_user(session, callback_query.from_user.id)
        if len(search_list) >= 3:
            await callback_query.message.edit_text(
                    text=txt_us.negative,
                    reply_markup=await search_keyboard_delete()
            )
            return
        else:
            await message_answer_process(bot, callback_query,
                                         state, txt_us.search, back_keyboard)
            await state.set_state(PostStates.wait_product_search)


@dp.callback_query(lambda c: c.data == 'products_search')
@subscribed_call
async def search_products(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «🔍Лист ожидания»
    """
    await message_answer_process(bot, callback_query,
                                 state, txt_us.info_search, keyboard=await search_keyboard())


@dp.callback_query(lambda c: c.data == 'list_search')
@logger.catch
@subscribed_call
async def list_search(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «📋Список товаров в листе ожидания»
    """
    list_data = []
    async for session in get_async_session():
        list_search = await SearchListRepository.get_search_by_user(session, callback_query.from_user.id)
        if len(list_search) == 0:
            await message_answer_process(bot, callback_query,
                                         state, 'У вас нет товаров в листе ожидания')
            return
        for search in list_search:
            msg = await callback_query.message.answer(text=search.name,
                                                      reply_markup=await delete_search_keyboard(search.id))
            list_data.append(msg.message_id)
        await state.update_data(list_search=list_data)


@dp.callback_query(lambda c: c.data.startswith('del_search'))
@logger.catch
async def del_search(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Удалить»
    для удаления товара из листа ожидания
    """
    id_search = int(callback_query.data.split('_')[2])
    async for session in get_async_session():
        await SearchListRepository.search_delete(session, id_search)
        await callback_query.message.edit_text(text='Товар удалён')


@dp.callback_query(lambda c: c.data.startswith('message_del_'))
async def del_search(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки подтверждения удаления сообщения из группы
    """
    message_id = callback_query.data.split('_')[2]
    await delete_message(bot, -1002090610085, int(message_id))
    await message_answer_process(bot, callback_query, state,
                                 "Ваше сообщение удалено",
                                 back_keyboard)

@dp.callback_query(lambda c: c.data.startswith('add_post'))
@subscribed_call
async def add_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопки для добавления поста
    """
    data = callback_query.data
    method = data.split('_')[2]
    user_id = callback_query.from_user.id
    if method == "free":
        async for session in get_async_session():
            user = await UserRepository.get_user_tg(user_id, session)
            if user.count_free_posts >= 10:
                await message_answer_process(bot, callback_query, state,
                                             "Вы достигли лимита бесплатных постов - 10.\n"
                                             "Теперь Вам недоступен этот способ публикации",
                                             back_keyboard)
                return
    await state.update_data(method=method)
    text = dict_text[method]
    await message_answer_process(bot, callback_query,
                                 state, text, back_keyboard)
    await state.set_state(PostStates.wait_name)


@dp.callback_query(lambda c: c.data.startswith('all_posts'))
@logger.catch
@subscribed_call
async def post_list(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «📋Мои объявления»
    """
    list_data = []
    async for session in get_async_session():
        posts = await PostRepository.get_posts_by_user(session, callback_query.from_user.id)
        if len(posts) == 0:
            await message_answer_process(bot, callback_query,
                                         state, 'У вас нет постов и публикаций', back_keyboard)
            return
        for post in posts:
            text = await create_text_by_post(post)
            try:
                file_path = os.path.join(os.getcwd(), MEDIA_DIR, post.photo)
            except FileNotFoundError as ex:
                pass
            else:
                msg = await callback_query.message.answer_photo(caption=text, photo=FSInputFile(file_path),
                                                                reply_markup=await post_keyboard(post.id, post.active),
                                                                parse_mode='Markdown')
                list_data.append(msg.message_id)
        await state.update_data(list_posts=list_data)


@dp.callback_query(lambda c: c.data.startswith('my-post_delete'))
@logger.catch
async def del_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Удалить пост навсегда»
    """
    id_post = int(callback_query.data.split('_')[2])
    async for session in get_async_session():
        post = await PostRepository.get_post(session, id_post)
        if all((post.url_message, post.channel_id)):
            chat_id = post.channel_id.split('_')[0]
            id_message = post.url_message.split('/')[4]
            id_main_message = post.url_message_main.split('/')[4]
            id_free_message = post.url_message_free.split('/')[4]
            file_path = os.path.join(os.getcwd(), MEDIA_DIR, post.photo)
            try:
                os.remove(file_path)
            except FileNotFoundError as ex:
                pass
            await PostRepository.post_delete(session, id_post)
            if post.active:
                await delete_message(bot, chat_id, id_message)
                if id_main_message != id_message:
                    await delete_message(bot, chat_id, id_main_message)
                if id_free_message != id_message:
                    await delete_message(bot, chat_id, id_free_message)

        await message_answer_process(bot, callback_query, state, "Пост удалён!", await reply_keyboard())
        try:
            await callback_query.message.delete()
        except TelegramBadRequest as ex:
            pass


@dp.callback_query(lambda c: c.data.startswith('my-post_deactivate'))
@logger.catch
async def deactivate_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Снять с публикации»
    """
    id_post = int(callback_query.data.split('_')[2])
    async for session in get_async_session():
        post = await PostRepository.get_post(session, id_post)
        if all((post.active, post.url_message, post.channel_id)):
            chat_id = post.channel_id.split('_')[0]
            id_message = post.url_message.split('/')[4]
            id_main_message = post.url_message_main.split('/')[4]
            id_free_message = post.url_message_free.split('/')[4]
            await delete_message(bot, chat_id, id_message)
            if id_main_message != id_message:
                await delete_message(bot, chat_id, id_main_message)
            if id_free_message != id_message:
                await delete_message(bot, chat_id, id_free_message)
        await PostRepository.update_post(session, id_post, active=False)
        await message_answer_process(bot, callback_query, state, "Пост снят с публикации",
                                     await reply_keyboard())


@dp.callback_query(lambda c: c.data.startswith('public_again'))
@subscribed_call
async def public_my_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать »
    """
    id_post = int(callback_query.data.split('_')[2])
    keyboard = await my_post_public_keyboard(id_post)
    text = "Выберите, как вы хотите опубликовать пост"
    await message_answer_process(bot, callback_query,
                                 state, text, keyboard)


@dp.message(PostStates.wait_product_search)
async def process_product_name(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки названия товара для листа ожидания
    """
    user_id = message.from_user.id
    async for session in get_async_session():
        if contains_emoji(message.text) or not 3 <= len(message.text) <= 75:
            await message_answer_process(bot, message, state,
                                         'Неправильный формат названия товара\n'
                                         'Попробуйте ещё раз', back_keyboard)
            return
        try:
            await message_answer_process(bot, message, state, txt_us.positive.format(name=message.text),
                                         back_keyboard)
        except TelegramBadRequest as ex:
            await message_answer_process(bot, message, state,
                                         'Неправильный формат названия товара\n'
                                         'Попробуйте ещё раз', back_keyboard)
        else:
            await SearchListRepository.create_search(session, user_id, message.text)
            await state.clear()


def contains_emoji(text: str) -> bool:
    # Функция возвращает True, если в тексте есть эмодзи, иначе False
    return bool(emoji.demojize(text) != text)


@dp.message(PostStates.wait_name)
async def process_product_name(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки названия товара для публикации поста
    """
    name = message.text
    is_valid = True
    dict_valid = {True: txt_us.save_name,
                  False: txt_us.name_invalid}
    try:
        pattern = r'^[a-zA-Z0-9-а-яА-ЯёЁ\s-]{4,75}$'
        if contains_emoji(name) or not await validate_string(pattern, name):
            is_valid = False
    except (ValueError, AttributeError, TypeError) as ex:
        is_valid = False
    else:
        if is_valid:
            await state.update_data(product_name=name)
            await state.set_state(PostStates.wait_photo)
    finally:
        await message_answer_process(bot, message, state, dict_valid[is_valid], back_keyboard)


async def save_file(bot: Bot, photo, state: FSMContext):
    """
    Функция, которая проверяет, что отправленная картинка
    не более MAX_SIZE_FILE
    Если да, то сохраняет файл в MEDIA_DIR
    """
    file_id = photo.file_id
    file_info = await bot.get_file(file_id)
    file_size = file_info.file_size
    if file_size > MAX_SIZE_FILE:
        return False
    file_extension = file_info.file_path.split('.')[-1]
    date_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    unique_filename = date_time + '.' + file_extension
    file_path = os.path.join(MEDIA_DIR, unique_filename)
    await bot.download_file(file_info.file_path, file_path)
    await state.update_data(product_photo=unique_filename)
    return True


@dp.message(DeletePost.wait_url_post)
async def wait_url_post(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки ссылки на удаление поста
    """
    username = message.from_user.username
    url = message.text
    if 'http' not in url:
        await message_answer_process(bot, message, state,
                                     "Неправильный формат ссылки, попробуйте ещё раз",
                                     None)
        return
    async for session in get_async_session():
        post = await PostRepository.get_post_by_url(session, url)
        if post and all((post.url_message, post.channel_id,
                         post.user_telegram == message.from_user.id)):
            chat_id = post.channel_id.split('_')[0]
            id_message = post.url_message.split('/')[4]
            id_main_message = post.url_message_main.split('/')[4]
            id_free_message = post.url_message_free.split('/')[4]
            file_path = os.path.join(os.getcwd(), MEDIA_DIR, post.photo)
            try:
                os.remove(file_path)
            except FileNotFoundError as ex:
                pass
            await PostRepository.post_delete(session, post.id)
            if post.active:
                await delete_message(bot, chat_id, id_message)
                if id_main_message != id_message:
                    await delete_message(bot, chat_id, id_main_message)
                if id_free_message != id_message:
                    await delete_message(bot, chat_id, id_free_message)
                await message_answer_process(bot, message, state,
                                             "Пост удалён",
                                             None)
                await state.set_state(None)
                return
        elif post:
            await message_answer_process(bot, message, state,
                                         "Вы не можете удалить этот пост, так как он опубликован не Вами",
                                         None)
            await state.set_state(None)
            return
    try:
        id_message = url.split('/')[5]
        msg = await bot.forward_message(chat_id=message.from_user.id,
                                        from_chat_id=-1002090610085,
                                        message_id=int(id_message))
    except (IndexError, TelegramBadRequest, TelegramForbiddenError) as ex:
        await message_answer_process(bot, message, state,
                                     "Ваше сообщение не найдено или Вы отправили нам неправильный"
                                     "формат ссылки",
                                     None)
    else:
        if username not in msg.caption:
            await asyncio.sleep(1)
            await delete_message(bot, message.from_user.id, msg.message_id)
            await message_answer_process(bot, message, state,
                                         "Вы не можете удалить это сообщение, так как в нём нет"
                                         "упоминания Вашего никнейма!",
                                         None)
        else:
            await asyncio.sleep(1)
            await delete_message(bot, message.from_user.id, msg.message_id)
            await message_answer_process(bot, message, state,
                                         "Удалить сообщение из группы?",
                                         await delete_message_keyboard(id_message))
    await state.set_state(None)


@dp.message(PostStates.wait_photo, F.content_type == 'photo')
async def process_product_photo(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки фотографии товара
    """
    photo = message.photo[-1]
    data = await state.get_data()
    save = await save_file(bot, photo, state)
    product_name = data.get('product_name')
    dict_text = {True: txt_us.save_photo.format(product_name=product_name),
                 False: txt_us.photo_cancell}
    text = dict_text[save]
    await message_answer_process(bot, message, state, text, back_keyboard)
    if save:
        await state.set_state(PostStates.wait_price)


@dp.message(PostStates.wait_photo)
async def process_invalid_photo(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки фотографии товара
    """
    await message_answer_process(bot, message, state, txt_us.photo_error, back_keyboard)


@dp.message(PostStates.wait_price)
async def process_product_price(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки цены на товар на маркетплейсе
    """
    dict_text = {True: txt_us.discount_price,
                 False: "Цена должна быть числом и не должна быть меньше или равна нулю.\n"
                        " Попробуйте ещё раз. Вводите цену без пробелов и знаков препинания"}
    try:
        product_price = int(message.text.replace(' ', ''))
        is_number = 0 < product_price < 300_000
    except (ValueError, AttributeError, TypeError) as ex:
        is_number = False
    text = dict_text[is_number]
    await message_answer_process(bot, message, state, text, back_keyboard)
    if is_number:
        await state.set_state(PostStates.wait_discount)
        await state.update_data(product_price=product_price)


@dp.message(PostStates.wait_discount)
async def process_product_discount(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки цены на товар с учётом скидки на него
    """
    dict_text = {True: txt_us.marketplace,
                 False: "Цена со скидкой(Кэшбеком) должна быть числом "
                        "и не должна быть меньше нуля и быть больше стоимости товара.\n"
                        "Попробуйте ещё раз ввести цену(без пробелов и знаков препинания)."}
    keyboard = await marketpalce_choice()
    dict_keyboard = {True: keyboard, False: back_keyboard}
    data = await state.get_data()
    price = data.get('product_price')
    try:
        discount_price = int(message.text.replace(' ', ''))
        is_number = 0 <= discount_price < 300_000 and int(100 - discount_price / price * 100) >= 15
    except (ValueError, AttributeError, TypeError) as ex:
        is_number = False
    text = dict_text[is_number]
    await message_answer_process(bot, message, state, text, dict_keyboard[is_number])
    if is_number:
        await state.update_data(price_discount=discount_price,
                                discount_proc=int(100 - discount_price / price * 100)
                                )
        await state.set_state(PostStates.wait_marketplace)


@dp.message(F.text.in_({'WB', 'OZON'}), PostStates.wait_marketplace)
async def marketplace(message: Message, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку при выборе маркетплейса,
    на котором размещён товар
    """
    mp = message.text
    keyboard_user = await username_keyboard(message.from_user.username)
    await message_answer_process(bot, message, state, txt_us.url_acc, keyboard_user)
    await state.update_data(product_marketplace=mp)
    await state.set_state(PostStates.wait_url_account)


async def validate_string(pattern, s):
    return bool(re.match(pattern, s))


@dp.message(PostStates.wait_url_account)
async def account_url(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки ссылки на аккаунт, с которым
    будут связываться покупатели
    """
    data = await state.get_data()
    url_acc = message.text
    keyboard_next = await channel_choice()
    keyboard_user = await username_keyboard(message.from_user.username)
    is_valid = True
    dict_valid = {
            True: (txt_us.channel, keyboard_next),
            False: ("Неверный ввод!\nВведите имя пользователя "
                    "телеграм без ссылок и значка '@'\n"
                    "Длина никнейма должна быть от 5 до 32 символов"
                    "Отправьте исправленные данные ещё раз "
                    "либо нажмите /start", keyboard_user)}

    try:
        pattern = r'^[a-zA-Z0-9_]{5,32}$'
        if not await validate_string(pattern, url_acc):
            is_valid = False
    except (ValueError, AttributeError, TypeError) as ex:
        is_valid = False
    else:
        if is_valid:
            await state.update_data(account_url=message.text)
            await state.set_state(PostStates.wait_channel)
    finally:
        await message_answer_process(bot, message, state,
                                     dict_valid[is_valid][0],
                                     dict_valid[is_valid][1])


@dp.callback_query(lambda c: c.data.startswith('channel'), PostStates.wait_channel)
@logger.catch
async def choice_group(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки выбора канала для публикации
    """
    data = callback_query.data
    user_id = callback_query.from_user.id
    channel_id = data.split(':')[1]
    name_channel = channels.get(channel_id)
    user_data = await state.get_data()
    if name_channel == 'Товары бесплатно' and user_data.get('discount_proc') != 100:
        await callback_query.message.edit_text(text="Вы не можете опубликовать объявление в этот канал,"
                                                    "так как ваш кэшбек меньше 100%. Выберите другой канал "
                                                    "или нажмите /start",
                                               reply_markup=await channel_choice())
        return
    await callback_query.message.edit_text(text=txt_us.channel_success.format(name=name_channel),
                                           parse_mode='Markdown')
    caption = txt_us.public_user.format(
            name=user_data.get('product_name'),
            value=int(user_data.get('product_price')) - int(user_data.get('price_discount')),
            discount=user_data.get('discount_proc'),
            price_discount=user_data.get('price_discount'),
            marketplace=user_data.get('product_marketplace'),
            url=user_data.get('account_url'), price=int(user_data.get('product_price'))
    )
    file_path = os.path.join(os.getcwd(), MEDIA_DIR, user_data.get('product_photo'))
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл по пути {file_path} не найден")
    await bot.send_photo(chat_id=user_id, photo=FSInputFile(file_path),
                         caption=caption)
    msg = await bot.send_message(user_id, text=txt_us.post_ready, reply_markup=await finish_public())
    await state.update_data(last_bot_message=msg.message_id,
                            channel=str(channel_id))


# async def public_again_post(chat_id, pos):
#     post =


async def public_post_in_channel(chat_id, photo_path, text, theme_id) -> str:
    """
    Функция для опубликования поста в выбранный канал/группу
    """
    file_path = os.path.join(os.getcwd(), MEDIA_DIR, photo_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл по пути {file_path} не найден")
    msg = await bot.send_photo(chat_id=chat_id, photo=FSInputFile(file_path), caption=text,
                               reply_to_message_id=theme_id)
    return msg.get_url()


@logger.catch
async def public_and_create_post(session, callback_query, data, state, method):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    text = await create_text_for_post(data)
    dict_post_params = await create_dict_params(data, user_id)
    chat_id, theme_id = data.get('channel').split('_')
    dict_post_params['method'] = method
    main_theme = int(theme_id) != 12955
    free_theme = int(theme_id) != 325 and int(data.get('discount_proc')) == 100
    if method != 'money':
        url = await public_post_in_channel(chat_id, data.get('product_photo'),
                                           text, theme_id)
        if main_theme:
            url_main_theme = await public_post_in_channel(chat_id, data.get('product_photo'),
                                                          text, 12955)
        else:
            url_main_theme = url
        if free_theme:
            url_free_theme = await public_post_in_channel(chat_id, data.get('product_photo'),
                                                          text, 325)
        else:
            url_free_theme = url
        await message_answer_process(bot, callback_query, state, txt_us.post_success.format(url=url),
                                     back_keyboard)
        await create_post_user(session, bot, **dict_post_params,
                               active=True, url_message=url, url_message_free=url_free_theme,
                               url_message_main=url_main_theme)
        await SellerRepository.seller_add(session)
        await PostRepository.increment_liquid_posts(session, {f'current_{method}': 1})
        await send_messages_for_admin(session, bot_admin, url, username)
    else:
        post_id = await create_post_user(session, bot, **dict_post_params)
        order = await OrderRepository.create_order(session, 1000, user_id, username, post_id)
        payment_url = await get_url_payment(order.id, 1000, "Размещение поста в группе")
        logger.info(f"Публикация нового поста за рубли. Пост - {post_id} Заказ - {order}. Ссылка -  {payment_url}")
        await message_answer_process(bot, callback_query, state, txt_us.post_payment.format(url=payment_url))


@logger.catch
async def public_and_update_post(session, callback_query, state, data, post):
    _, method, id_post = callback_query.data.split('_')
    username = callback_query.from_user.username
    user_id = callback_query.from_user.id
    date_public = datetime.today().date()
    date_expired = date_public + timedelta(days=7)
    chat_id, theme_id = post.channel_id.split('_')
    main_theme = int(theme_id) != 12955
    free_theme = int(theme_id) != 325 and int(data.get('discount_proc')) == 100
    text = await create_text_for_post(data)
    if method != 'money':
        url = await public_post_in_channel(chat_id, post.photo, text, theme_id)
        logger.info(f"Публикация поста - {url}")
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
        await message_answer_process(bot, callback_query, state, txt_us.post_success.format(url=url))
        await message_answer_process(bot, callback_query, state, txt_us.post_success.format(url=url))
        await PostRepository.update_post(session, int(id_post), active=True,
                                         date_expired=date_expired, date_public=date_public,
                                         url_message=url, method=method, url_message_main=url_main_theme,
                                         url_message_free=url_free_theme)
        await PostRepository.increment_liquid_posts(session, {f'current_{method}': 1})
        await SellerRepository.seller_add(session)
        await send_messages_for_admin(session, bot_admin, url, username)
    else:
        order = await OrderRepository.create_order(session, 1000, user_id, username, post.id)
        payment_url = await get_url_payment(order.id, 1000, "Размещение поста в группе")
        logger.info(f"Публикация истекшего поста за рубли Заказ - {order}. Ссылка -  {payment_url}")
        await message_answer_process(bot, callback_query, state, txt_us.post_payment.format(url=payment_url))


@dp.callback_query(lambda c: c.data == 'finish_public', PostStates.wait_channel)
@logger.catch
async def finish(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать»
    """
    user_id = callback_query.from_user.id
    data = await state.get_data()
    method = data.get('method')
    logger.info(f"Размещение поста. Метод - {method}")
    async for session in get_async_session():
        if method == 'free':
            await public_and_create_post(session, callback_query, data, state, method)
        elif method == 'coins':
            success = await public_for_coins(user_id, 10000, session)
            if success:
                await BankRepository.bank_update(session, 10000)
                await public_and_create_post(session, callback_query, data, state, method)
            else:
                await message_answer_process(bot, callback_query, state, txt_us.not_coins)
        else:
            await public_and_create_post(session, callback_query, data, state, method)
    await state.clear()


@dp.callback_query(lambda c: c.data.startswith('again'))
@logger.catch
async def again_public(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать »
    """
    id_post = callback_query.data.split('_')[2]
    method = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    async for session in get_async_session():
        user = await UserRepository.get_user_tg(user_id, session)
        post = await PostRepository.get_post(session, int(id_post))
        data = {'product_name': post.name,
                'product_price': post.price,
                'price_discount': post.discounted_price,
                'product_marketplace': post.marketplace,
                'account_url': post.account_url,
                'discount_proc': post.discount
                }
        if method == 'free':
            if post.method != 'free':
                await message_answer_process(bot, callback_query, state,
                                             'Вы не можете опубликовать пост в этот канал бесплатно.\n'
                                             'Создайте новый пост')
                return
            if user.count_free_posts >= 10:
                await message_answer_process(bot, callback_query, state,
                                             'Вы достигли лимита публикации бесплатных постов - 10\n'
                                             'Выберите другой способ публикации')
                return
            await public_and_update_post(session, callback_query, state, data, post)
        elif method == 'coins':
            success = await public_for_coins(user_id, 10000, session)
            if success:
                await BankRepository.bank_update(session, 10000)
                await public_and_update_post(session, callback_query, state, data, post)
            else:
                await message_answer_process(bot, callback_query, state, txt_us.not_coins)
        else:
            await public_and_update_post(session, callback_query, state, data, post)


@dp.message()
async def handle_message(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        topic_number = message.reply_to_message.message_id if message.reply_to_message else 0
        if topic_number == 12955 and message.photo:
            async for session in get_async_session():
                await PostRepository.increment_liquid_posts(session, {'current_free': 1})
                await SellerRepository.seller_add(session)
                search_posts = await UserRepository.get_users_with_search(session)
                url = f"https://t.me/Buyer_Marketplace/{topic_number}/{message.message_id}"
                await notification(search_posts, message.caption, url, bot)


async def get_channel_id_by_url(url: str) -> str:
    """
    Функция получения ID канала по его url
    """
    channel_id = url.split("//")[-1].split("/")[1]
    return f'@{channel_id}'


@logger.catch
async def check_task_complete(telegram_id: int, task_id: int) -> bool:
    """
    Функция для проверки выполнения задания
    """
    async for session in get_async_session():
        user = await UserRepository.get_user_with_tasks(telegram_id, session)
        task = await TaskRepository.get_task_by_id(task_id, session)
        if task in user.tasks:
            return True
        if task.category_id == 2:
            if await is_user_subscribed(telegram_id, await get_channel_id_by_url(task.url)):
                await TaskRepository.add_task(user, task, session)
                await PullRepository.update_pull(session, 5000, 'current_tasks')
                await user.update_count_coins(session, 5000, 'Выполнение задания')
                return True
            else:
                return False
        else:  # Пока что возвращаем True для всех остальных задач
            await TaskRepository.add_task(user, task, session)
            await PullRepository.update_pull(session, 5000, 'current_tasks')
            await user.update_count_coins(session, 5000, 'Выполнение задания')
            return True


# @dp.message(F.text)
# async def delete_unexpected_message(message: Message) -> None:
#     """
#     Функция для удаления ботом сообщений, которые он не ожидает,
#     или которые он не должен обрабатывать
#     Необходима для того, чтобы пользователь не засорял чат лишними сообщениями
#     :param message:
#     :return:
#     """
#     await asyncio.sleep(0.5)
#     await message.delete()


def run_web_server():
    os.system('python web_server.py')


def run_bot_admin():
    os.system('python bot_admin.py')


async def main():
    """
    Основная функция, запускающая бота, для пользователей
    и запускающая веб-сервер на aiogram для проверки подписок
    из веб-приложения и работы с приёмом оплаты
    :return:
    """
    # p_web = multiprocessing.Process(target=run_web_server)
    # p_admin = multiprocessing.Process(target=run_bot_admin)
    # p_web.start()
    # p_admin.start()
    subprocess.Popen(['python', 'web_server.py'])
    subprocess.Popen(['python', 'bot_admin.py'])
    await asyncio.sleep(2)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    # p_web.join()
    # p_admin.join()


if __name__ == "__main__":
    asyncio.run(main())
