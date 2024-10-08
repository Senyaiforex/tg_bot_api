import os
from loguru import logger
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.client.session import aiohttp
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards import *
import functools
from database import async_session
from states import PostStatesDelete, LiquidStates, SetPull, TaskStates, StatesUserActions, States
from repository import UserRepository, TaskRepository, PostRepository, BankRepository, PullRepository
from utils.bot_utils.messages import message_answer_process
from utils.bot_utils.text_static import txt_adm
from utils.bot_utils.util import get_info_from_user, create_text_transactions, get_info_users, \
    valid_date, create_statistic_message, create_text_pull, create_text_friends, \
    change_active_user


async def get_async_session() -> async_session:
    async with async_session() as session:
        yield session


logger.add("logs/logs_admin/log_file.log",
           retention="5 days",
           rotation='18:00',
           compression="zip",
           level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | "
                  "{level: <8} | "
                  "{name}:{function}:{line} - "
                  "{message}")

MEDIA_DIR = 'media'
BOT_TOKEN = os.getenv("ADMIN_TOKEN")

dict_keyboards = {
        '🗒Добавить задание': ('Выберите тип задания, которое хотите добавить', select_type_task),
        '📉Статистика': ('Выберите дальнейшее действие', inline_statistics),
        # '➕Добавить пост': '',
        # '🗑Удалить пост': '',
}

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def permissions_check(func):
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        async for session in get_async_session():
            user = await UserRepository.get_user_tg(user_id, session)
            if not user or all((user.admin == False, user.superuser == False)):
                await message.answer(txt_adm.message_no_access)
                return
            return await func(message, session, *args, **kwargs)

    return wrapper


@dp.message(Command("start"))
@logger.catch
@permissions_check
async def start(message: Message, session) -> None:
    """
    Функция обработки команды /start, для начала работы с ботом
    """
    picture = FSInputFile('static/start_pic.jpg')
    user_id = message.from_user.id
    superuser = None
    async for session in get_async_session():
        user = await UserRepository.get_user_tg(user_id, session)
        if not user or all((user.admin == False, user.superuser == False)):
            await bot.send_photo(user_id, caption=txt_adm.message_no_access,
                                 photo=picture)
            return
        superuser = user.superuser
    caption = txt_adm.message_superuser if superuser else txt_adm.message_for_admin
    keyboard = await menu_admin(superuser)
    await bot.send_photo(chat_id=user_id, photo=picture,
                         caption=caption,
                         reply_markup=keyboard, parse_mode='Markdown')


@dp.message(F.text.in_(dict_keyboards))
@permissions_check
async def inline_buttons_menu(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопки меню
    """
    await state.set_state(None)
    text, func = dict_keyboards[message.text]
    keyboard = await func()
    await message_answer_process(bot, message, state, text, keyboard, False)


@dp.message(F.text == "В меню")
@logger.catch
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.set_state(state=None)  # Завершаем текущее состояние
    user_id = message.from_user.id
    superuser = None
    async for session in get_async_session():
        user = await UserRepository.get_user_tg(user_id, session)
        if not user or all((user.admin == False, user.superuser == False)):
            await bot.send_message(user_id, text=txt_adm.message_no_access)
            return
        superuser = user.superuser
    text = txt_adm.message_superuser if superuser else txt_adm.message_for_admin
    keyboard = await menu_admin(superuser)
    await message.answer(text=text, reply_markup=keyboard, parse_mode='Markdown')


@dp.message(F.text == '👥Добавить администратора')
@permissions_check
async def add_admin(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 👥Добавить администратора
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.add_telegram,
                                 back_keyboard, False)
    await state.set_state(States.wait_telegram_admin)


@dp.message(F.text == '➖Удалить администратора')
@permissions_check
async def delete_admin(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку ➖Удалить администратора
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.add_telegram,
                                 back_keyboard, False)
    await state.set_state(States.wait_username_admin_block)


@dp.message(F.text == '💰Пул наград')
@logger.catch
@permissions_check
async def pull_info(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 💰Пул
    """
    await state.set_state(None)
    pull = await PullRepository.get_pull(session)
    text = await create_text_pull(pull)
    await message_answer_process(bot, message, state,
                                 text + "\nВыберите тип пула, который хотите изменить",
                                 await type_pulls_keyboard(), False)


@dp.message(F.text == '💵Банк монет')
@logger.catch
@permissions_check
async def get_bank(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 💵Банк монет
    """
    await state.set_state(None)
    bank_summ = await BankRepository.get_bank_coins(session)
    await message_answer_process(bot, message, state,
                                 txt_adm.bank_text.format(amount=bank_summ),
                                 back_keyboard, False)


@dp.message(F.text == '📔Ликвидность на публикации')
@logger.catch
@permissions_check
async def liquid_info(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 📔Ликвидность на публикации
    """
    await state.set_state(None)
    today = datetime.today().date()
    free, token, coins, money, stars = await PostRepository.get_count_posts_with_types(session,
                                                                                       today,
                                                                                       'month')
    liquid_posts = await PostRepository.get_liquid_posts(session)
    dict_info = {
            'need_free': liquid_posts.free_posts, 'need_coins': liquid_posts.coins_posts,
            'need_token': liquid_posts.token_posts, 'need_money': liquid_posts.money_posts,
            'need_stars': liquid_posts.stars_posts,
            'current_free': free, 'current_coins': coins, 'current_token': token, 'current_money': money,
            'current_stars': stars
    }
    text = txt_adm.text_liquid.format(**dict_info) + "\nВыберите тип ликвидности, которую хотите изменить"

    await message_answer_process(bot, message, state,
                                 text, await type_liquid_keyboard(), False)


@dp.message(F.text == '🚫Блокировать')
@permissions_check
async def block_user(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 🚫Блокировать
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.block_username,
                                 back_keyboard, False)
    await state.set_state(StatesUserActions.wait_username_block)


@dp.message(F.text == '✅Разблокировать')
@permissions_check
async def unlock_user(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку ✅Разблокировать
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.unlock_username,
                                 back_keyboard, False)
    await state.set_state(StatesUserActions.wait_username_unlock)


@dp.message(F.text == '🗑Удалить пост')
@permissions_check
async def post_delete_full(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 🗑Удалить пост
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.post_delete_url,
                                 back_keyboard, False)
    await state.set_state(PostStatesDelete.wait_url)


@dp.message(F.text == '➖Удалить задание')
@permissions_check
async def task_delete_full(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку ➖Удалить задание
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.task_delete_url,
                                 back_keyboard, False)
    await state.set_state(TaskStates.wait_url_delete)


@dp.message(F.text == '🔥Сжечь монеты')
@permissions_check
async def remission_coins(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 🔥Сжечь монеты
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 'Введите количество монет, которые хотите сжечь',
                                 back_keyboard, False)
    await state.set_state(States.wait_delete_coins)


@dp.callback_query(lambda c: c.data.startswith('confirm_remission_'))
async def set_liquid(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Изменить пул ликвидности»
    """
    size = callback_query.data.split('_')[2]
    dict_info = {True: f"Вы сожгли *{size}* монет из банка монет",
                 False: "У Вас недостаточно монет в банке для сжигания"}
    async for session in get_async_session():
        bank_update = await BankRepository.delete_coins(session, int(size))
    await callback_query.message.edit_text(text=dict_info[bank_update],
                                           reply_markup=back_menu,
                                           parse_mode='Markdown'
                                           )


@dp.callback_query(lambda c: c.data.startswith('menu'))
async def add_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку В меню
    """
    await state.set_state(None)
    picture = FSInputFile('static/start_pic.jpg')
    user_id = callback_query.from_user.id
    superuser = None
    async for session in get_async_session():
        user = await UserRepository.get_user_tg(user_id, session)
        if not user or all((user.admin == False, user.superuser == False)):
            await bot.send_photo(user_id, caption=txt_adm.message_no_access,
                                 photo=picture)
            return
        superuser = user.superuser
    caption = txt_adm.message_superuser if superuser else txt_adm.message_for_admin
    keyboard = await menu_admin(superuser)
    await bot.send_photo(chat_id=user_id, photo=picture,
                         caption=caption,
                         reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.message.delete()


@dp.callback_query(lambda c: c.data.startswith('task'))
async def add_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Добавить задание»
    """
    await message_answer_process(bot, callback_query, state,
                                 txt_adm.task_description,
                                 back_keyboard, False)
    type_task = callback_query.data.split('_')[1]
    await state.set_state(TaskStates.wait_descript)
    await state.update_data(type_task=type_task)


@dp.callback_query(lambda c: c.data.startswith('all_info_users'))
@logger.catch
async def statistic_users(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Статистика по всем пользователям»
    """
    text = ''
    async for session in get_async_session():
        dict_info = await get_info_users(session)
        for msg, value in dict_info.items():
            text += f'{msg} - {value}\n'
        await callback_query.message.edit_text(text=text)


@dp.callback_query(lambda c: c.data.startswith("info_pull"))
async def info_pull_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на inline-кнопку Назад при работе с пулом
    """
    await state.set_state(None)
    async for session in get_async_session():
        pull = await PullRepository.get_pull(session)
        text = await create_text_pull(pull)
    await callback_query.message.edit_text(text=text + "\nВыберите тип пула, который хотите изменить",
                                           reply_markup=await type_pulls_keyboard(),
                                           parse_mode='Markdown')


@dp.callback_query(lambda c: c.data.startswith("info_liquid"))
async def liquid_info_callback(message: Message, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на inline-кнопку Назад при работе с ликвидностью
    """
    await state.set_state(None)
    today = datetime.today().date()
    async for session in get_async_session():
        free, token, coins, money, stars = await PostRepository.get_count_posts_with_types(session,
                                                                                           today,
                                                                                           'month')
        liquid_posts = await PostRepository.get_liquid_posts(session)
        dict_info = {
                'need_free': liquid_posts.free_posts, 'need_coins': liquid_posts.coins_posts,
                'need_token': liquid_posts.token_posts, 'need_money': liquid_posts.money_posts,
                'need_stars': liquid_posts.stars_posts,
                'current_free': free, 'current_coins': coins, 'current_token': token, 'current_money': money,
                'current_stars': stars
        }
        text = txt_adm.text_liquid.format(**dict_info)

        await message_answer_process(bot, message, state,
                                     text + '\nВыберите тип ликвидности, которую хотите изменить',
                                     await type_liquid_keyboard(), False)


@dp.callback_query(lambda c: c.data.startswith('info_user'))
async def info_user(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Информация о пользователе»
    """
    await message_answer_process(bot, callback_query, state,
                                 txt_adm.info_username,
                                 back_keyboard, False)
    await state.set_state(StatesUserActions.wait_username)


@dp.callback_query(lambda c: c.data.startswith('transactions'))
@logger.catch
async def info_user(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Все транзакции»
    """
    telegram_id = int(callback_query.data.split('_')[1])
    async for session in get_async_session():
        text = await create_text_transactions(telegram_id, session)
        await message_answer_process(bot, callback_query, state,
                                     text, back_keyboard, False)


@dp.callback_query(lambda c: c.data.startswith('friends'))
@logger.catch
async def info_user_friends(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Друзья»
    """
    telegram_id = int(callback_query.data.split('_')[1])
    async for session in get_async_session():
        friends = await UserRepository.get_friends(telegram_id, session)
        text = await create_text_friends(friends)
        await message_answer_process(bot, callback_query, state,
                                     text, back_keyboard, False)


@dp.callback_query(lambda c: c.data == 'info_posts')
@logger.catch
async def info_posts(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Статистика по постам»
    """
    async for session in get_async_session():
        text = await create_statistic_message(session, bot)
        await message_answer_process(bot, callback_query, state,
                                     text, back_keyboard, False)


@dp.callback_query(lambda c: c.data.startswith("pull_"))
async def set_pull_by_type(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на одну из inline-кнопок «типа пула»
    """
    dict_pull = {'coins': (SetPull.wait_coins, 'Введите пул на монеты'),
                 'friends': (SetPull.wait_friends, 'Введите пул на друзей'),
                 'tasks': (SetPull.wait_task, 'Введите пул на задания'),
                 'plan': (SetPull.wait_plan, 'Введите пул на краудсорсинг'),
                 'farming': (SetPull.wait_farming, 'Введите пул на фарминг')}
    type_pull = callback_query.data.split('_')[1]
    state_pull = dict_pull[type_pull][0]
    await message_answer_process(bot, callback_query, state,
                                 dict_pull[type_pull][1],
                                 back_keyboard, False)
    await state.set_state(state_pull)


@dp.callback_query(lambda c: c.data.startswith('liquid_'))
@logger.catch
async def set_liquid(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку для изменения ликвидности
    """
    dict_liquid = {'coins': (LiquidStates.wait_coins, 'Введите ликвидность постов за монеты'),
                   'token': (LiquidStates.wait_token, 'Введите ликвидность постов за токены'),
                   'stars': (LiquidStates.wait_stars, 'Введите ликвидность постов за звёзды'),
                   'money': (LiquidStates.wait_money, 'Введите ликвидность постов за рубли'),
                   'free': (LiquidStates.wait_free, 'Введите ликвидность постов бесплатно')}
    type_liquid = callback_query.data.split('_')[1]
    state_liquid = dict_liquid[type_liquid][0]
    await message_answer_process(bot, callback_query, state,
                                 dict_liquid[type_liquid][1],
                                 back_keyboard, False)
    await state.set_state(state_liquid)


@dp.message(PostStatesDelete.wait_url)
@logger.catch
async def wait_url_post_block(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки url для удаления поста
    """
    post = message.text
    async for session in get_async_session():
        try:
            current_url = post.split('/')
            current_url.pop(4)
        except IndexError as ex:
            return
        url_post = '/'.join(current_url)
        post = await PostRepository.get_post_by_url(session, url_post)
        if not post:
            await message_answer_process(bot, message, state,
                                         'Такого сообщения в группе нет!', None, False)
            return
        chat_id = post.channel_id.split('_')[0]
        id_message = post.url_message.split('/')[4]
        id_message_main = post.url_message_main.split('/')[4]
        id_message_free = post.url_message_free.split('/')[4]
        file_path = os.path.join(os.getcwd(), MEDIA_DIR, post.photo)
        keyboard = back_keyboard
        async with aiohttp.ClientSession() as session_aio:
            response_url = await session_aio.get(f'http://bot:8443/delete_message/{chat_id}/{id_message}')
            if id_message_main != id_message:
                response_main = await session_aio.get(f'http://bot:8443/delete_message/{chat_id}/{id_message_main}')
                if response_url.status == 200 and response_main.status == 200:
                    await message_answer_process(bot, message, state,
                                                 'Пост успешно удалён!', keyboard, False)
                else:
                    await message_answer_process(bot, message, state,
                                                 'Пост удалить не получилось,'
                                                 ' попробуйте сделать это вручную!', keyboard, False)
            else:
                if response_url.status == 200:
                    await message_answer_process(bot, message, state,
                                                 'Пост успешно удалён!', keyboard, False)
                else:
                    await message_answer_process(bot, message, state,
                                                 'Удалить пост из группы не получилось,'
                                                 ' попробуйте сделать это вручную!', keyboard, False)
            if id_message_free != id_message:
                await session_aio.get(f'http://bot:8443/delete_message/{chat_id}/{id_message_free}')
        try:
            os.remove(file_path)
        except FileNotFoundError as ex:
            pass
        await PostRepository.post_delete(session, post.id)
        await state.set_state(None)


@dp.message(TaskStates.wait_url_delete)
@logger.catch
async def wait_url_task_delete(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки url для удаления задания
    """
    url_task = message.text
    async for session in get_async_session():
        task = await TaskRepository.get_task_by_url(session, url_task)
        if not task:
            text = "Такого задания нет! Попробуйте ещё раз"
            await message.delete()
        else:
            text = "Задание успешно удалено!"
        await TaskRepository.task_delete(session, task.id)
        await message_answer_process(bot, message, state,
                                     text, back_keyboard, False)
        await state.set_state(None)


@dp.message(States.wait_telegram_admin)
@permissions_check
async def add_telegram_admin(message: Message, session, state: FSMContext) -> None:
    """
    Функция обработки отправки telegram ID пользователя,
    для добавления его в администраторы
    """
    msg = message.text
    if not msg.isdigit():
        text = txt_adm.telegram_id_invalid
    else:
        text = txt_adm.username_add
        await state.set_state(States.wait_username)
        await state.update_data(telegram_admin=int(msg))
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)


@dp.message(States.wait_username)
@logger.catch
@permissions_check
async def add_username_admin(message: Message, session, state: FSMContext) -> None:
    """
    Функция обработки отправки username пользователя,
    для добавления его в администраторы
    """
    msg = message.text
    data = await state.get_data()
    telegram_admin = data.get('telegram_admin')
    text = txt_adm.admin_add_success.format(name=msg)
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)
    await UserRepository.create_user_admin(telegram_admin, msg, session)
    await state.set_state(None)


@dp.message(States.wait_username_admin_block)
@logger.catch
@permissions_check
async def wait_username_admin_delete(message: Message, session, state: FSMContext) -> None:
    """
    Функция обработки отправки username пользователя,
    для удаления его из администраторов
    """
    msg = message.text
    dict_info = {True: f"Пользователь удалён из администраторов!",
                 False: "Такой пользователь отсутствует в базе данных"}
    success = await UserRepository.delete_user_admin(msg, session)
    await message_answer_process(bot, message, state,
                                 dict_info[success], back_keyboard, False)
    await state.set_state(None)


@dp.message(TaskStates.wait_descript)
async def wait_description(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки описания задания для его добавления
    """
    description = message.text
    text = txt_adm.task_add_url
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)
    await state.update_data(description=description)
    await state.set_state(TaskStates.wait_url)


@dp.message(TaskStates.wait_url)
@permissions_check
async def wait_url(message: Message, session, state: FSMContext) -> None:
    """
    Функция обработки отправки url задания для его добавления
    """
    url = message.text
    if 'http' not in url:
        text = txt_adm.task_add_url
    else:
        text = txt_adm.task_add_date
        await state.update_data(url=url)
        await state.set_state(TaskStates.wait_date)
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)


@dp.message(TaskStates.wait_date)
@logger.catch
@permissions_check  # Просто прокинуть сессию
async def wait_date(message: Message, session, state: FSMContext) -> None:
    """
    Функция обработки отправки даты, до которой действует задание
    """
    data = await state.get_data()
    date = message.text
    if not await valid_date(date):
        text = txt_adm.task_date_invalid
    else:
        text = txt_adm.task_add_success
        type_task, description, url = (data.get('type_task'),
                                       data.get('description'),
                                       data.get('url'))
        await TaskRepository.create_task(url, description, type_task, date, session)
        await state.set_state(None)

    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)


@dp.message(StatesUserActions.wait_username)
@logger.catch
async def username_info(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки username пользователя, о котором
    необходимо получить информацию
    """
    username = message.text
    keyboard = None
    async for session in get_async_session():
        dict_info = await get_info_from_user(username, session)
        if not dict_info:
            text = txt_adm.user_username_invalid
        else:
            text = ""
            for msg, value in dict_info.items():
                text += f'{msg} - {value}\n'
            keyboard = await user_info_keyboard(dict_info['Телеграм id пользователя'])
        await message_answer_process(bot, message, state,
                                     text, keyboard if keyboard else back_keyboard, False)
        await state.set_state(None)


@dp.message(StatesUserActions.wait_username_block)
@logger.catch
async def block_user_by_name(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки username пользователя, которого
    необходимо заблокировать
    """
    username = message.text
    async for session in get_async_session():
        block = await change_active_user(username, False, session)
        if not block:
            text = txt_adm.user_username_invalid
        else:
            text = txt_adm.user_block_success.format(username=username.replace('_', '\_'))
        await message_answer_process(bot, message, state,
                                     text, back_keyboard, False)
        await state.set_state(None)


@dp.message(StatesUserActions.wait_username_unlock)
@logger.catch
async def unlock_user_by_name(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки username пользователя, которого
    необходимо разблокировать
    """
    username = message.text
    async for session in get_async_session():
        block = await change_active_user(username, True, session)
        if not block:
            text = txt_adm.user_username_invalid
        else:
            text = txt_adm.user_unlock_success.format(username=username.replace('_', '\_'))
        await message_answer_process(bot, message, state,
                                     text, back_keyboard, False)
        await state.set_state(None)


@logger.catch
async def process_pull(message: Message, state: FSMContext,
                       data_key):
    """
    Функция обработки параметров пула для его добавления
    """
    keyboard = back_keyboard
    size = message.text.replace(' ', '')
    if not size.isdigit():
        text = txt_adm.add_pull_invalid
    else:
        dict_pull = {'coins': 'монеты', 'farming': 'фарминг',
                     'friends': 'друзей', 'tasks': 'задачи',
                     'plan': 'краудсорсинг'}
        text = f"Установлен новый пул на {dict_pull[data_key]} - *{size}*"
        keyboard = await back_to_pull()
        await state.set_state(None)
        async for session in get_async_session():
            await PullRepository.set_pull_size({data_key: int(size)}, session)

    await state.update_data(**{data_key: size})
    await message_answer_process(bot, message, state,
                                 text, keyboard, False)


@dp.message(States.wait_delete_coins)
async def wait_count_delete_coins(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения монет для сжигания
    """
    keyboard = back_keyboard
    size = message.text.replace(' ', '')
    if not size.isdigit():
        text = "Вы ввели неверное количество монет для сжигания"
    else:
        keyboard = await remission_coins_keyboard(size)
        text = f"Вы уверены, что хотите сжечь *{size}* монет?"
    await message_answer_process(bot, message, state,
                                 text, keyboard, False)


@dp.message(SetPull.wait_farming)
async def wait_farm(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на фарминг
    """
    await process_pull(message, state, 'farming')


@dp.message(SetPull.wait_task)
async def wait_task(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на задания
    """
    await process_pull(message, state, 'tasks')


@dp.message(SetPull.wait_friends)
async def wait_friends(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на друзей
    """
    await process_pull(message, state, 'friends')


@dp.message(SetPull.wait_plan)
async def wait_plan(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на краудсорсинг
    """
    await process_pull(message, state, 'plan')


@dp.message(SetPull.wait_coins)
async def wait_coins(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на монеты
    если значение валидно, то создаётся новый пул в базе данных
    """
    await process_pull(message, state, 'coins')


async def process_liquid(message: Message,
                         state: FSMContext,
                         data_key):
    """
    Функция обработки параметров ликвидности публикаций для добавления
    """
    keyboard = back_keyboard
    size = message.text.replace(' ', '')
    if not size.isdigit() or int(size) <= 0:
        text = txt_adm.liquid_invalid
    else:
        dict_pull = {'free': 'бесплатно', 'coins': 'за монеты',
                     'token': 'за токены', 'stars': 'за звёзды',
                     'money': 'за рубли'}
        text = f"Установлено новое значение пула ликвидности на посты {dict_pull[data_key]} - *{int(size)}*"
        keyboard = await back_to_liquid()
        await state.set_state(None)
        async for session in get_async_session():
            await PostRepository.update_liquid_posts(session,
                                                     {data_key + '_posts': int(size)})

    await state.update_data(**{data_key: size})
    await message_answer_process(bot, message, state,
                                 text, keyboard, False)


@dp.message(LiquidStates.wait_free)
async def wait_free(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на бесплатные посты
    """
    await process_liquid(message, state, 'free')


@dp.message(LiquidStates.wait_coins)
async def wait_coins(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на посты за монеты
    """
    await process_liquid(message, state, 'coins')


@dp.message(LiquidStates.wait_token)
async def wait_token(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на посты за токены
    """
    await process_liquid(message, state, 'token')


@dp.message(LiquidStates.wait_stars)
async def wait_stars(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на посты за звёзды
    """
    await process_liquid(message, state, 'stars')


@dp.message(LiquidStates.wait_money)
@logger.catch
async def wait_money(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на посты за рубли
    """
    await process_liquid(message, state, 'money')


async def main():
    """
    Основная функция, запускающая бота-администратора
    """
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
