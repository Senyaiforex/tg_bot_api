import os
import logging
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.client.session import aiohttp
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from keyboards import *
import functools
from database import async_session
from repository import UserRepository, TaskRepository, PostRepository, BankRepository, PullRepository
from utils import get_info_users
from utils.bot_utils.messages import message_answer_process
from utils.bot_utils.text_static import txt_adm
from utils.bot_utils.util import get_info_from_user, create_text_transactions, \
    block_user_by_username, valid_date, create_statistic_message, create_text_pull, create_text_friends


async def get_async_session() -> async_session:
    async with async_session() as session:
        yield session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MEDIA_DIR = 'media'
BOT_TOKEN = "7279689856:AAGp9CToYaxJYWZdCL8YG7nxZ1orddKWdlQ"

dict_keyboards = {
        '🗒Добавить задание': ('Выберите тип задания, которое хотите добавить', select_type_task),
        '📉Статистика': ('Выберите дальнейшее действие', inline_statistics),
        # '➕Добавить пост': '',
        # '🗑Удалить пост': '',
}


class States(StatesGroup):
    wait_descript = State()
    wait_url = State()
    wait_date = State()
    confirmation = State()
    wait_telegram_admin = State()
    wait_username = State()
    wait_telegram_block = State()
    wait_type = State()


class SetPull(StatesGroup):
    wait_farming = State()
    wait_task = State()
    wait_friends = State()
    wait_plan = State()
    wait_coins = State()


class StatesInfo(StatesGroup):
    wait_username = State()
    wait_username_block = State()


class PostStates(StatesGroup):
    wait_url = State()


class TaskStates(StatesGroup):
    wait_url_delete = State()


class LiquidStates(StatesGroup):
    wait_free = State()
    wait_coins = State()
    wait_money = State()
    wait_token = State()
    wait_stars = State()


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


@dp.message(F.text == "Вернуться")
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
    await message.answer(text=text, reply_markup=keyboard)


@dp.message(F.text == '👥Добавить администратора')
@permissions_check
async def inline_buttons_menu(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 👥Добавить администратора
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.add_telegram,
                                 back_keyboard, False)
    await state.set_state(States.wait_telegram_admin)


@dp.message(F.text == '💰Пул')
@permissions_check
async def pull_info(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 💰Пул
    """
    await state.set_state(None)
    pull = await PullRepository.get_pull(session)
    if not pull:
        text = 'Текущий пулл пуст'
    else:
        text = await create_text_pull(pull)
    await message_answer_process(bot, message, state,
                                 text,
                                 await pull_keyboard(), False)


@dp.message(F.text == '💵Банк монет')
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
    text = txt_adm.text_liquid.format(**dict_info)

    await message_answer_process(bot, message, state,
                                 text, await liquid_posts_keyboard(), False)


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
    await state.set_state(StatesInfo.wait_username_block)


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
    await state.set_state(PostStates.wait_url)


@dp.message(F.text == '➖Удалить задание')
@permissions_check
async def post_delete_full(message: Message, session, state: FSMContext) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку 🗑Удалить пост
    """
    await state.set_state(None)
    await message_answer_process(bot, message, state,
                                 txt_adm.task_delete_url,
                                 back_keyboard, False)
    await state.set_state(TaskStates.wait_url_delete)


@dp.callback_query(lambda c: c.data == 'set_pull')
async def set_pull(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «установить пулл»
    """
    await message_answer_process(bot, callback_query, state,
                                 txt_adm.farming,
                                 back_keyboard, False)
    await state.set_state(SetPull.wait_farming)


@dp.callback_query(lambda c: c.data == 'set_liquid')
async def set_liquid(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Изменить пул ликвидности»
    """
    await message_answer_process(bot, callback_query, state,
                                 txt_adm.free,
                                 back_keyboard, False)
    await state.set_state(LiquidStates.wait_free)


@dp.callback_query(lambda c: c.data.startswith('task'))
async def add_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Добавить задание»
    """
    await message_answer_process(bot, callback_query, state,
                                 txt_adm.task_description,
                                 back_keyboard, False)
    type_task = callback_query.data.split('_')[1]
    await state.set_state(States.wait_descript)
    await state.update_data(type_task=type_task)


@dp.callback_query(lambda c: c.data.startswith('all_info_users'))
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


@dp.callback_query(lambda c: c.data.startswith('info_user'))
async def info_user(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Информация о пользователе»
    """
    await message_answer_process(bot, callback_query, state,
                                 txt_adm.info_username,
                                 back_keyboard, False)
    await state.set_state(StatesInfo.wait_username)


@dp.callback_query(lambda c: c.data.startswith('confirm_pull'))
async def confirm_pull(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Да»
    которая подтверждает установление нового пулла
    """
    data = await state.get_data()
    dict_pull_sizes = {
            'farming': data.get('farming'), 'coins': data.get('coins'),
            'task': data.get('task'), 'plan': data.get('plan'),
            'friends': data.get('friends'),
    }

    async for session in get_async_session():
        await PullRepository.set_pull_size(dict_pull_sizes, session)
    await message_answer_process(bot, callback_query, state,
                                 txt_adm.pull_set_success,
                                 back_keyboard, False)


@dp.callback_query(lambda c: c.data.startswith('confirm_liquid'))
async def confirm_liquid(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Да»
    которая подтверждает установление нового пула ликвидности публикаций
    """
    data = await state.get_data()
    dict_liquid_sizes = {
            'free_posts': data.get('free'), 'coins_posts': data.get('coins'),
            'money_posts': data.get('money'), 'token_posts': data.get('token'),
    }

    async for session in get_async_session():
        await PostRepository.update_liquid_posts(session, **dict_liquid_sizes)
    await message_answer_process(bot, callback_query, state,
                                 "Установлено новое значение пула ликвидности!",
                                 back_keyboard, False)


@dp.callback_query(lambda c: c.data.startswith('transactions'))
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
async def info_posts(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Функция обработки нажатия на inline-кнопку «Статистика по постам»
    """
    async for session in get_async_session():
        text = await create_statistic_message(session, bot)
        await message_answer_process(bot, callback_query, state,
                                     text, back_keyboard, False)


@dp.message(PostStates.wait_url)
async def wait_url_post_block(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки url для блокировки поста
    """
    post = message.text
    async for session in get_async_session():
        current_url = post.split('/')
        current_url.pop(4)
        url_post = '/'.join(current_url)
        post = await PostRepository.get_post_by_url(session, url_post)
        if not post:
            await message_answer_process(bot, message, state,
                                         'Такого сообщения в группе нет!', None, False)
        chat_id = post.channel_id.split('_')[0]
        id_message = post.url_message.split('/')[4]
        id_message_main = post.url_message_main.split('/')[4]
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
        os.remove(file_path)
        await PostRepository.post_delete(session, post.id)
        await state.set_state(None)


@dp.message(TaskStates.wait_url_delete)
async def wait_url_task_block(message: Message, state: FSMContext) -> None:
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
@permissions_check
async def add_username_admin(message: Message, session, state: FSMContext) -> None:
    """
    Функция обработки отправки username пользователя,
    для добавления его в администраторы
    """
    msg = message.text
    data = await state.get_data()
    if '_' in msg:
        msg.replace('_', '\_')
    telegram_admin = data.get('telegram_admin')
    text = txt_adm.admin_add_success.format(name=msg)
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)
    await UserRepository.create_user_admin(telegram_admin, msg, session)
    await state.set_state(None)


@dp.message(States.wait_descript)
async def wait_description(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки описания задания для его добавления
    """
    description = message.text
    text = txt_adm.task_add_url
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)
    await state.update_data(description=description)
    await state.set_state(States.wait_url)


@dp.message(States.wait_url)
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
        await state.set_state(States.wait_date)
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)


@dp.message(States.wait_date)
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


@dp.message(StatesInfo.wait_username)
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


@dp.message(StatesInfo.wait_username_block)
async def block_user_by_name(message: Message, state: FSMContext) -> None:
    """
    Функция обработки отправки username пользователя, которого
    необходимо заблокировать
    """
    username = message.text
    async for session in get_async_session():
        block = await block_user_by_username(username, session)
        if not block:
            text = txt_adm.user_username_invalid
        else:
            if '_' in username:
                username.replace('_', '\_')
            text = txt_adm.user_block_success.format(username=username)
        await message_answer_process(bot, message, state,
                                     text, back_keyboard, False)
        await state.set_state(None)


async def process_pull(message: Message, state: FSMContext,
                       data_key, next_state, prompt_text):
    """
    Функция обработки параметров пула для его добавления
    """
    size = message.text.replace(' ', '')
    if not size.isdigit():
        text = txt_adm.add_pull_invalid
    else:
        text = txt_adm.pull_input_success.format(
                size=size,
                key=prompt_text[0],
                next_key=prompt_text[1]
        )
    await state.set_state(next_state)
    await state.update_data(**{data_key: size})
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)


@dp.message(SetPull.wait_farming)
async def wait_farm(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на фарминг
    """
    await process_pull(message, state, 'farming',
                       SetPull.wait_task, ('фарминг', 'задания'))


@dp.message(SetPull.wait_task)
async def wait_task(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на задания
    """
    await process_pull(message, state, 'task',
                       SetPull.wait_friends, ('задания', 'друзей'))


@dp.message(SetPull.wait_friends)
async def wait_friends(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на друзей
    """
    await process_pull(message, state, 'friends',
                       SetPull.wait_plan, ('друзей', 'краудсорсинг'))


@dp.message(SetPull.wait_plan)
async def wait_plan(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на краудсорсинг
    """
    await process_pull(message, state, 'plan',
                       SetPull.wait_coins, ('краудсорсинг', 'монеты'))


@dp.message(SetPull.wait_coins)
async def wait_coins(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения пула на монеты
    если значение валидно, то создаётся новый пул в базе данных
    """
    data = await state.get_data()
    size = message.text
    farming = data.get('farming')
    task = data.get('task')
    plan = data.get('plan')
    friends = data.get('friends')
    keyboard = None
    if not size.isdigit():
        text = txt_adm.add_pull_invalid
    elif not all([farming, task, friends, plan]):
        text = txt_adm.pull_empty
    else:
        text = txt_adm.pull_new_success.format(
                size=size, plan=plan, task=task,
                friends=friends, farming=farming
        )
        keyboard = await menu_pull_confirm()
        await state.update_data(coins=size)
    await state.set_state(None)
    await state.update_data(coins=size)
    await message_answer_process(bot, message, state,
                                 text, keyboard if keyboard else back_keyboard, False)


async def process_liquid(message: Message, state: FSMContext,
                         data_key, next_state, prompt_text):
    """
    Функция обработки параметров ликвидности публикаций для добавления
    """
    size = message.text.replace(' ', '')
    if not size.isdigit() or int(size) <= 0:
        text = txt_adm.liquid_invalid
    else:
        text = txt_adm.liquid_input_success.format(
                size=size,
                key=prompt_text[0],
                next_key=prompt_text[1]
        )
    await state.set_state(next_state)
    await state.update_data(**{data_key: size})
    await message_answer_process(bot, message, state,
                                 text, back_keyboard, False)


@dp.message(LiquidStates.wait_free)
async def wait_free(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на бесплатные посты
    """
    await process_pull(message, state, 'free',
                       LiquidStates.wait_coins, ('посты бесплатно', 'постов за монеты'))


@dp.message(LiquidStates.wait_coins)
async def wait_coins(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на посты за монеты
    """
    await process_pull(message, state, 'coins',
                       LiquidStates.wait_token, ('посты за монеты', 'постов за токены'))


@dp.message(LiquidStates.wait_token)
async def wait_token(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на посты за токены
    """
    await process_pull(message, state, 'token',
                       LiquidStates.wait_stars, ('посты за токены', 'постов за звёзды'))


@dp.message(LiquidStates.wait_stars)
async def wait_stars(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности на посты за звёзды
    """
    await process_pull(message, state, 'stars',
                       LiquidStates.wait_money, ('посты за звёзды', 'постов за рубли'))


@dp.message(LiquidStates.wait_money)
async def result_liquid(message: Message, state: FSMContext) -> None:
    """
    Функция обработки значения ликвидности постов за рубли
    если значение валидно, то ликвидность на публикацию постов обновляется в базе данных
    """
    data = await state.get_data()
    size = message.text
    free, token, coins, stars = data.get('free'), data.get('token'), data.get('coins'), data.get('stars')
    keyboard = None
    if not size.isdigit() or int(size) <= 0:
        text = txt_adm.liquid_invalid
    elif not all((free, token, coins)):
        text = txt_adm.liquid_empty
    else:
        text = txt_adm.liquid_new_success.format(
                free=free, token=token, coins=coins,
                money=size, stars=stars
        )
        keyboard = await menu_liquid_confirm()
    await state.set_state(None)
    await state.update_data(money=size)
    await message_answer_process(bot, message, state,
                                 text, keyboard if keyboard else back_keyboard, False)


async def main():
    """
    Основная функция, запускающая бота-администратора
    """
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
