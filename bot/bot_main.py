import multiprocessing
import asyncio
import os
import emoji
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
import functools
from bot_admin import bot as bot_admin
from payment import get_url_payment
from keyboards import *
from database import async_session
from repository import UserRepository, TaskRepository, PostRepository, OrderRepository, SearchListRepository, \
    BankRepository, PullRepository
import subprocess
import logging
from utils.bot_utils.messages import process_menu_message, message_answer_process, delete_message, reply_keyboard, \
    send_messages_for_admin
from utils.bot_utils.util import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MEDIA_DIR = 'media'
MAX_SIZE_FILE = int(1.5 * 1024 * 1024)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


os.makedirs(MEDIA_DIR, exist_ok=True)
BOT_TOKEN = "7006667556:AAFzRm7LXS3VoyqCIvN5QJ-8RRsixZ9uPek"
CHANNEL_ID = '@Buyer_Marketplace'
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
web_app_url = 'https://tg-botttt.netlify.app'


async def is_user_subscribed(user_id: int, channel_id: str) -> bool:
    """
    Функция проверки, что пользователь с user_id подписан на канал channel_id
    """
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
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


@dp.message(F.text == "Вернуться")
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.set_state(state=None)  # Завершаем текущее состояние
    picture = FSInputFile('static/start_pic.jpg')
    user_id = message.from_user.id
    text = "Добро пожаловать!\n"
    keyboard_reply = await start_reply_keyboard()
    await bot.send_photo(user_id, caption=text, photo=picture, parse_mode='Markdown',
                         reply_markup=keyboard_reply)


@dp.message(F.text == 'Меню')
@subscribed
async def menu(message: Message, state: FSMContext) -> None:
    """
    Функция обработки нажатия на кнопку «Меню»
    """
    await state.set_state(None)
    picture = FSInputFile('static/menu_pic.jpg')
    keyboard = await menu_keyboard()
    await process_menu_message(picture, keyboard, bot, message, state)


@dp.message(F.text == 'Опубликовать пост')
@subscribed
async def public(message: Message, state: FSMContext) -> None:
    """
    Функция обработки нажатия на кнопку «Опубликовать пост»
    """
    await state.set_state(None)
    picture = FSInputFile('static/public_pic.jpg')
    keyboard = await public_keyboard()
    await process_menu_message(picture, keyboard, bot, message, state)


@dp.message(F.text == 'Каталог')
@subscribed
async def catalog(message: Message, state: FSMContext) -> None:
    """
    Функция обработки нажатия на кнопку «Каталог»
    """
    await state.set_state(None)
    picture = FSInputFile('static/catalog_pic.jpg')
    keyboard = await catalog_keyboard()
    await process_menu_message(picture, keyboard, bot, message, state)


@dp.callback_query(lambda c: c.data == 'back_to_menu')
async def back_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Вернуться в меню»
    """
    await state.set_state(None)
    picture = FSInputFile('static/menu_pic.jpg')
    keyboard = await menu_keyboard()
    await process_menu_message(picture, keyboard, bot, callback_query, state)


@dp.callback_query(lambda c: c.data == 'public')
async def add_post_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать пост»
    """
    picture = FSInputFile('static/public_pic.jpg')
    keyboard = await public_keyboard()
    await process_menu_message(picture, keyboard, bot,
                               callback_query, state,
                               txt_us.cooperation)


@dp.callback_query(lambda c: c.data == 'catalog')
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
async def search_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «➕Добавить товар в лист ожидания»
    """
    await message_answer_process(bot, callback_query,
                                 state, txt_us.search, back_keyboard)
    await state.set_state(PostStates.wait_product_search)


@dp.callback_query(lambda c: c.data == 'products_search')
async def search_products(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «🔍Лист ожидания»
    """

    await message_answer_process(bot, callback_query,
                                 state, txt_us.info_search, keyboard=await search_keyboard())


@dp.callback_query(lambda c: c.data == 'list_search')
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
async def del_search(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Удалить»
    для удаления товара из листа ожидания
    """
    id_search = callback_query.data.split('_')[2]
    async for session in get_async_session():
        await SearchListRepository.search_delete(session, id_search)
        await callback_query.message.edit_text(text='Товар удалён')


@dp.callback_query(lambda c: c.data.startswith('add_post'))
async def add_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопки для добавления поста
    """
    data = callback_query.data
    method = data.split('_')[2]
    await state.update_data(method=method)
    await message_answer_process(bot, callback_query,
                                 state, txt_us.name_product, back_keyboard)
    await state.set_state(PostStates.wait_name)


@dp.callback_query(lambda c: c.data.startswith('all_posts'))
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
            file_path = os.path.join(os.getcwd(), MEDIA_DIR, post.photo)
            msg = await callback_query.message.answer_photo(caption=text, photo=FSInputFile(file_path),
                                                            reply_markup=await post_keyboard(post.id,
                                                                                             post.active))
            list_data.append(msg.message_id)
        await state.update_data(list_posts=list_data)


@dp.callback_query(lambda c: c.data.startswith('my-post_delete'))
async def del_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Удалить пост навсегда»
    """
    id_post = callback_query.data.split('_')[2]
    async for session in get_async_session():
        post = await PostRepository.get_post(session, id_post)
        if all((post.url_message, post.channel_id)):
            chat_id = post.channel_id.split('_')[0]
            id_message = post.url_message.split('/')[4]
            id_main_message = post.url_message_main.split('/')[4]
            file_path = os.path.join(os.getcwd(), MEDIA_DIR, post.photo)
            os.remove(file_path)
            await PostRepository.post_delete(session, id_post)
            if post.active:
                await delete_message(bot, chat_id, id_message)
                if id_main_message != id_message:
                    await delete_message(bot, chat_id, id_main_message)
        await message_answer_process(bot, callback_query, state, "Пост удалён!", await reply_keyboard())
        await callback_query.message.delete()


@dp.callback_query(lambda c: c.data.startswith('my-post_deactivate'))
async def deactivate_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Снять с публикации»
    """
    id_post = callback_query.data.split('_')[2]
    async for session in get_async_session():
        post = await PostRepository.get_post(session, id_post)
        if all((post.active, post.url_message, post.channel_id)):
            chat_id = post.channel_id.split('_')[0]
            id_message = post.url_message.split('/')[4]
            id_main_message = post.url_message_main.split('/')[4]
            await delete_message(bot, chat_id, id_message)
            if id_main_message != id_message:
                await delete_message(bot, chat_id, id_main_message)
        await PostRepository.update_post(session, id_post, active=False)
        await message_answer_process(bot, callback_query, state, "Пост снят с публикации",
                                     await reply_keyboard())


@dp.callback_query(lambda c: c.data.startswith('public_again'))
async def public_my_post(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать »
    """
    id_post = callback_query.data.split('_')[2]
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
    dict_text = {True: txt_us.positive.format(name=message.text),
                 False: txt_us.negative}
    async for session in get_async_session():
        search_cr = await SearchListRepository.create_search(session, user_id, message.text)
        await state.clear()
        await message_answer_process(bot, message, state, dict_text[search_cr], back_keyboard)


def contains_emoji(text: str) -> bool:
    # Функция возвращает True, если в тексте есть эмодзи, иначе False
    return bool(emoji.demojize(text) != text)


@dp.message(PostStates.wait_name)
async def process_product_name(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки названия товара для публикации поста
    """
    name = message.text
    if len(name) > 75 or contains_emoji(name):
        await message_answer_process(bot, message, state, txt_us.name_invalid)
        return
    await state.update_data(product_name=message.text)
    await message_answer_process(bot, message, state, txt_us.save_name, back_keyboard)
    await state.set_state(PostStates.wait_photo)


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
                 False: "Цена должна быть числом и не должна быть меньше или равна нулю. Попробуйте ещё раз."}
    product_price = message.text
    is_number = product_price.isdigit() and int(product_price) > 0
    text = dict_text[is_number]
    await message_answer_process(bot, message, state, text, back_keyboard)
    if is_number:
        await state.set_state(PostStates.wait_discount)
        await state.update_data(product_price=int(product_price))


@dp.message(PostStates.wait_discount)
async def process_product_discount(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки цены на товар с учётом скидки на него
    """
    dict_text = {True: txt_us.marketplace,
                 False: "Цена со скидкой(Кэшбеком) должна быть числом "
                        "и не должна быть меньше нуля и быть меньше стоимости товара. Попробуйте ещё раз."}
    keyboard = await marketpalce_choice()
    dict_keyboard = {True: keyboard, False: back_keyboard}
    discount_price = message.text
    data = await state.get_data()
    price = data.get('product_price')
    is_number = all((discount_price.isdigit(), int(discount_price) >= 0,
                     int(100 - (int(discount_price) / price * 100)) > 15))  # Все условия соблюдены
    text = dict_text[is_number]
    await message_answer_process(bot, message, state, text, dict_keyboard[is_number])
    if is_number:
        await state.update_data(price_discount=int(discount_price),
                                discount_proc=int(100 - (int(message.text) / price * 100)))
        await state.set_state(PostStates.wait_marketplace)


@dp.message(F.text.in_({'WB', 'OZON', 'Пропустить'}), PostStates.wait_marketplace)
async def marketplace(message: Message, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку при выборе маркетплейса,
    на котором размещён товар
    """
    mp = message.text
    if mp == 'Пропустить':
        mp = 'Нет'
    await message_answer_process(bot, message, state, txt_us.url_acc, back_keyboard)
    await state.update_data(product_marketplace=mp)
    await state.set_state(PostStates.wait_url_account)


@dp.message(PostStates.wait_url_account)
async def account_url(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки ссылки на аккаунт, с которым
    будут связываться покупатели
    """
    data = await state.get_data()
    url_acc = message.text
    keyboard = await channel_choice(method=data.get('method'))
    if any(['@' in url_acc, 'http' in url_acc, '-' in url_acc, '/' in url_acc]):
        await message_answer_process(bot, message, state,
                                     "Неверный ввод!\nВведите имя пользователя "
                                     "телеграм без ссылок и значка '@'"
                                     "Отправьте исправленные данные ещё раз "
                                     "либо нажмите /start", keyboard)
    await state.update_data(account_url=message.text)
    await message_answer_process(bot, message, state, txt_us.channel, keyboard)
    await state.set_state(PostStates.wait_channel)


@dp.callback_query(lambda c: c.data.startswith('channel'), PostStates.wait_channel)
async def choice_group(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки выбора канала для публикации
    """
    data = callback_query.data
    user_id = callback_query.from_user.id
    channel_id = data.split(':')[1]
    name_channel = channels.get(channel_id, 'Товары бесплатно')
    await callback_query.message.edit_text(text=txt_us.channel_success.format(name=name_channel),
                                           parse_mode='Markdown')
    user_data = await state.get_data()
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


async def public_and_create_post(session, callback_query, data, state, method):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    text = await create_text_for_post(data)
    dict_post_params = await create_dict_params(data, user_id)
    chat_id, theme_id = data.get('channel').split('_')
    dict_post_params['method'] = method
    main_theme = True if theme_id != 29 else False
    if method != 'money':
        url = await public_post_in_channel(chat_id, data.get('product_photo'),
                                           text, theme_id)
        if main_theme:
            url_main_theme = await public_post_in_channel(chat_id, data.get('product_photo'),
                                                          text, 29)
        else:
            url_main_theme = url
        await message_answer_process(bot, callback_query, state, txt_us.post_success.format(url=url),
                                     back_keyboard)
        await create_post_user(session, bot, **dict_post_params,
                               active=True, url_message=url,
                               url_message_main=url_main_theme)
        await send_messages_for_admin(session, bot_admin, url, username)
    else:
        post_id = await create_post_user(session, bot, **dict_post_params)
        order = await OrderRepository.create_order(session, 1000, user_id, username, post_id)
        payment_url = await get_url_payment(order.id, 1000, "Размещение поста в группе")
        await message_answer_process(bot, callback_query, state, txt_us.post_payment.format(url=payment_url))


async def public_and_update_post(session, callback_query, state, data, post):
    _, method, id_post = callback_query.data.split('_')
    username = callback_query.from_user.username
    user_id = callback_query.from_user.id
    date_public = datetime.today().date()
    date_expired = date_public + timedelta(days=7)
    chat_id, theme_id = post.channel_id.split('_')
    main_theme = True if theme_id != 29 else False
    text = await create_text_for_post(data)
    if method != 'money':
        url = await public_post_in_channel(chat_id, post.photo, text, theme_id)
        if main_theme:
            url_main_theme = await public_post_in_channel(chat_id, post.photo,
                                                          text, 29)
        else:
            url_main_theme = url
        await message_answer_process(bot, callback_query, state, txt_us.post_success.format(url=url))
        await message_answer_process(bot, callback_query, state, txt_us.post_success.format(url=url))
        await PostRepository.update_post(session, id_post, active=True,
                                         date_expired=date_expired, date_public=date_public,
                                         url_message=url, method=method, url_message_main=url_main_theme)
        await send_messages_for_admin(session, bot_admin, url, username)
    else:
        order = await OrderRepository.create_order(session, 1000, user_id, username, post.id)
        payment_url = await get_url_payment(order.id, 1000, "Размещение поста в группе")
        await message_answer_process(bot, callback_query, state, txt_us.post_payment.format(url=payment_url))


@dp.callback_query(lambda c: c.data == 'finish_public', PostStates.wait_channel)
async def finish(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать»
    """
    user_id = callback_query.from_user.id
    data = await state.get_data()
    method = data.get('method')
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
async def again_public(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Опубликовать »
    """
    id_post = callback_query.data.split('_')[2]
    method = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    async for session in get_async_session():
        post = await PostRepository.get_post(session, id_post)
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


async def get_channel_id_by_url(url: str) -> str:
    """
    Функция получения ID канала по его url
    """
    channel_id = url.split("//")[-1].split("/")[1]
    return f'@{channel_id}'


async def check_task_complete(telegram_id: int, task_id: int) -> bool:
    """
    Функция для проверки выполнения задания
    """
    async for session in get_async_session():
        user = await UserRepository.get_user_with_tasks(telegram_id, session)
        task = await TaskRepository.get_task_by_id(task_id, session)
        if task in user.tasks:
            return True
        if task.category_id == 1:
            if await is_user_subscribed(telegram_id, await get_channel_id_by_url(task.url)):
                await TaskRepository.add_task(user, task, session)
                await PullRepository.update_pull(session, 5000, 'current_task')
                await user.update_count_coins(session, 5000, 'Выполнение задания')
                return True
            else:
                return False
        else:  # Пока что возвращаем True для всех остальных задач
            await TaskRepository.add_task(user, task, session)
            await PullRepository.update_pull(session, 5000, 'current_task')
            await user.update_count_coins(session, 5000, 'Выполнение задания')
            return True


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
