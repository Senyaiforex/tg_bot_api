from datetime import datetime, timedelta
from difflib import SequenceMatcher
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import update

from .messages import send_message
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, friends, Post, Pull
from repository import UserRepository, PostRepository, TaskRepository, PullRepository, SellerRepository
from fastapi import HTTPException
from .text_static import *

CHANNEL_ID = os.getenv("CHANNEL_ID")


async def url_post_keyboard(url):
    menu_button = [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    button_url = [InlineKeyboardButton(text='Посмотреть товар',
                                   url=url)]
    return InlineKeyboardMarkup(inline_keyboard=[button_url, menu_button])


async def get_user_bot(telegram_id: int, session: AsyncSession):
    """
    Функция дял получения пользователя из базы данных по id_telegram
    :param telegram_id:
    :param session:
    :return:
    """
    result = await session.execute(select(User).where(User.id_telegram == telegram_id))
    user = result.scalars().first()
    return user


async def handle_invitation(inviter_id: int, user_id: int, username: str, session: AsyncSession) -> None:
    """
     Функция обработки приглашения пользователя
    :param inviter_id: ID пользователя, который пригласил.
    :param username: Никнейм пользователя.
    :param user_id: ID пользователя, который получил приглашение.
    :param session: Асинхронная сессия
    :return:
    """

    inviter = await session.execute(select(User).where(User.id_telegram == inviter_id))
    inviter = inviter.scalars().first()
    await inviter.update_count_coins(session, 5000, f"Приглашение друга")
    await inviter.set_friends(session, 1)
    new_user = User(id_telegram=user_id,
                    user_name=username,
                    rank_id=1)
    await new_user.update_count_coins(session, 5000, f"Бонус за регистрацию", new=True)
    await PullRepository.update_pull(session, 10000, "current_friends")
    session.add(new_user)
    await session.commit()
    await session.execute(friends.insert().values(
            friend1_id_telegram=inviter_id,
            friend2_id_telegram=user_id
    ))
    await session.commit()


async def get_info_users(session: AsyncSession) -> dict[str: int]:
    """
    Функция для получения информации по статистике пользователей
    :param session:
    :return:
    """
    dict_info = {}
    count_users, count_admins = (await UserRepository.get_count_users(session),
                                 await UserRepository.get_count_admins(session))
    today = datetime.today().date()
    count_users_date = await UserRepository.get_users_date(session, today)
    dict_info['Количество активных пользователей'] = count_users
    dict_info['Новых пользователей сегодня'] = count_users_date[0]
    dict_info['Новых пользователей за неделю'] = count_users_date[1]
    dict_info['Новых пользователей за месяц'] = count_users_date[2]
    dict_info['Количество администраторов'] = count_admins
    return dict_info


async def get_info_from_user(username: str, session: AsyncSession) -> dict[str: int | str]:
    """
    Функция для получения информации о пользователе по его username
    :param username: никнейм пользователя
    :param session:
    :return:
    """
    dict_info = {}
    try:
        user = await UserRepository.get_user_by_username(username, session)
    except HTTPException as ex:
        return dict_info
    username = user.user_name.replace("_", "\_")
    dict_info = {
            'Телеграм id пользователя': user.id_telegram,
            'Никнейм': f"@{username}",
            'Дата регистрации': user.registration_date.strftime('%d-%m-%Y'),
            'Количество токенов': user.count_coins,
            'Количество фарма': user.count_pharmd,
            'Уровень': user.rank.level,
            'Ранг': user.rank.rank.name,
            'Количество приглашенных друзей': user.count_invited_friends,
            'Количество покупок': user.purchase_count,
            'Количество продаж': user.sale_count,
            'Количество размещённых постов': len(user.posts),
            'Количество транзакций': len(user.history_transactions),
            'Количество выполненных задач': user.count_tasks,
            'Активный': 'Да' if user.active else 'Нет'
    }
    return dict_info


async def create_text_transactions(telegram_id: int, session) -> str:
    """
    Функция для получения текста сообщения со всеми транзакциями
    :param telegram_id:
    :param session:
    :return:
    """
    text = ""
    try:
        transactions = await UserRepository.get_transactions_by_id(telegram_id, 80, 0, session)
    except HTTPException as ex:
        return txt_adm.user_empty_transaction
    for transaction in transactions:
        text += txt_adm.user_transaction_info.format(
                date=transaction.transaction_date.strftime('%d-%m-%Y'),
                type_transaction=transaction.description,
                summ=transaction.change_amount
        )
    return text if text else "Транзакции у данного пользователя отсутствуют"


async def change_active_user(username: str, active: bool, session: AsyncSession) -> bool:
    """
    Функция для блокировки/разблокировки пользователя по его Username
    :param username:
    :param session:
    :return:
    """
    try:
        await UserRepository.update_active_user(username, active, session)
        return True
    except HTTPException as ex:
        return False


async def valid_date(date: str):
    try:
        datetime.strptime(date, '%d.%m.%Y')
        return True
    except (ValueError, TypeError, AttributeError):
        return False


async def similar(name_one: str, name_two: str) -> bool:
    similar_int = SequenceMatcher(None, name_one, name_two).ratio()
    if similar_int >= 0.35:
        return True
    else:
        return False


async def create_post_user(session, bot, **kwargs) -> bool:
    """
    Функция для создания нового поста
    :param session: Асинхронная сессия
    :param bot: экземпляр запущенного бота
    """
    name = kwargs.get('name')
    url = kwargs.get('url_message')
    active = kwargs.get('active', None)
    if active:
        date_public = datetime.today().date()
        kwargs['date_public'] = date_public
        kwargs['date_expired'] = date_public + timedelta(days=7)
    post = await PostRepository.create_post(session, **kwargs)
    if active:
        search_posts = await UserRepository.get_users_with_search(session)
        await notification(search_posts, name, url, bot)
        if kwargs.get('method') == 'free':
            await session.execute(
                    update(User)
                    .where(User.id_telegram == int(kwargs.get('user_telegram')))
                    .values(count_free_posts=User.count_free_posts + 1)
            )
            await session.commit()
    return post.id


async def update_active_post(session, bot, url, post_id):
    post = await PostRepository.get_post(session, post_id)
    await PostRepository.update_post(session,
                                     post_id, url_message=url,
                                     active=True, date_public=datetime.today().date())
    search_posts = await UserRepository.get_users_with_search(session)
    await notification(search_posts, post.name, url, bot)


async def notification(users: list[User], name, url, bot) -> None:
    for user in users:
        for post in user.search_posts:
            resemblance = await similar(name, post.name)
            if resemblance or post.name.lower() in name.lower() or name.lower() in post.name.lower():
                text = f"Появился новый товар, похожий на то, что Вы искали: *{name}*"
                await (send_message(bot, user.id_telegram,
                                    text, await url_post_keyboard(url)))


async def public_for_coins(telegram_id, count, session):
    coins = await UserRepository.get_count_coins(session, telegram_id)
    if coins < count:
        return False
    else:
        await UserRepository.change_coins_by_id(telegram_id, count,
                                                False, 'Публикация поста', session)
        return True


async def create_dict_params(data: dict, user_id):
    dict_post_params = {
            'name': data.get('product_name'),
            'price': int(data.get('product_price')),
            'discounted_price': int(data.get('price_discount')),
            'user_telegram': user_id,
            'account_url': data.get('account_url'),
            'photo': data.get('product_photo'),
            'marketplace': data.get('product_marketplace'),
            'discount': int(data.get('discount_proc')),
            # 'url_message': 'https://t.me/Buyer_Marketplace/190/7002'
            'channel_id': data.get('channel'),
    }
    return dict_post_params


async def create_text_for_post(data):
    text = txt_us.post.format(
            name=data.get('product_name'),
            value=data.get('product_price') - data.get('price_discount'),
            discount=data.get('discount_proc'),
            price=data.get('product_price'),
            price_discount=data.get('price_discount'),
            marketplace=data.get('product_marketplace', 'Нет'),
            url=data.get('account_url')
    )
    return text


async def create_text_by_post(post: Post):
    url = post.account_url.replace('_', '\_')
    text = txt_us.info_post.format(
            name=post.name,
            value=int(post.price) - int(post.discounted_price),
            discount=post.discount,
            price=post.price,
            price_discount=post.discounted_price,
            url=url
    )
    if post.marketplace:
        text += f'\nМаркетплейс: {post.marketplace}'
    if post.date_public:
        text += f'\nДата публикации: `{post.date_public.strftime("%d.%m.%Y")}`'
    if post.active:
        text += f'\nСтатус: ✅Опубликован до `{post.date_expired.strftime("%d.%m.%Y")}`'
    else:
        text += '\nСтатус: ⛔️Не опубликован'
    return text


async def create_statistic_message(session: AsyncSession, bot: Bot) -> str:
    count_members = await bot.get_chat_member_count(CHANNEL_ID)
    date = datetime.today().date()
    count_tasks = await TaskRepository.get_count_tasks(session, date)
    liquid_instance = await PostRepository.get_liquid_posts(session)
    count_month = sum(
            getattr(liquid_instance, attr) for attr
            in dir(liquid_instance) if attr.startswith("current")
    )
    count_posts = await PostRepository.get_count_post_by_time(session, date)
    sellers = await SellerRepository.get_count_sellers(session, date)
    text = txt_adm.post_statistic.format(
            count_sbs=count_members,
            posts_month=count_month,
            posts_today=count_posts[0] + sellers,
            count_tasks=count_tasks
    )
    return text


async def create_text_pull(pull: Pull):
    text_pull = txt_adm.text_pull.format(
            coins=pull.coins, current_coins=pull.current_coins,
            farming=pull.farming, current_farming=pull.current_farming,
            friends=pull.friends, current_friends=pull.current_friends,
            task=pull.tasks, current_task=pull.current_tasks,
            plan=pull.plan, current_plan=pull.current_plan
    )
    return text_pull


async def create_text_friends(friends: list) -> str:
    """
    Функция для создания текстового представления списка друзей
    :param friends: список пользователей
    :return:
    """
    text = ""
    if not friends:
        return txt_adm.user_empty_friends
    else:
        for friend in friends:
            username = friend["username"]
            text += txt_adm.user_friends_info.format(
                    username=username.replace("_", "\_"),
                    level=friend["level"],
                    rank=friend["rank"],
                    date=friend["date_registration"]
            )
        return text
