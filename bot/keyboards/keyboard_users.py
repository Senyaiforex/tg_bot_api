from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from utils.bot_utils.text_static import catalog_list, channels

group_url = 'https://t.me/Buyer_Marketplace'
manager_tg = 'https://t.me/Broker_113'


async def start_reply_keyboard():
    menu = [KeyboardButton(text="Меню")]
    keyboard = ReplyKeyboardMarkup(keyboard=[
            menu
    ], resize_keyboard=True, is_persistent=True, one_time_keyboard=False)
    return keyboard


async def start_keyboard():
    start_but = [InlineKeyboardButton(text='Подписаться', url=group_url)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[start_but])
    return keyboard


async def menu_keyboard():
    """
    Функция создаёт кнопки для меню
    :return: InlineKeyboardMarkup
    """
    add_post = [InlineKeyboardButton(text='📥 Разместить пост в группе',
                                     callback_data='public')]
    all_posts = [InlineKeyboardButton(text='📋Мои объявления', callback_data='all_posts')]
    catalog = [InlineKeyboardButton(text='📂 Каталог с товаром',
                                    callback_data='catalog')]
    search_prod = [InlineKeyboardButton(text='🔍Лист ожидания', callback_data='products_search')]
    delete_post_by_name = [InlineKeyboardButton(text='🗑Удалить объявление с моим упоминанием',
                                                callback_data='delete_post_by_name')]
    group = [InlineKeyboardButton(text='👥 Группа', url=group_url)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[add_post, all_posts, catalog,
                                                     search_prod, group, delete_post_by_name])
    return keyboard


async def catalog_keyboard():
    """
    Функция создаёт кнопки для каталога с товарами
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=elem[0],
                                                   url=elem[1])] for elem in catalog_list])
    keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='back_to_menu')]

    )
    return keyboard


async def public_keyboard():
    """
    Функция создаёт кнопки для размещения постов в группе
    :return: InlineKeyboardMarkup
    """
    free_post = [InlineKeyboardButton(text='Разместить пост бесплатно',
                                      callback_data='add_post_free')]
    coins_post = [InlineKeyboardButton(text='Разместить пост за монеты - 10 000 монет',
                                       callback_data='add_post_coins')]
    # tokens_post = [InlineKeyboardButton(text='Разместить пост за токены',
    #                                     callback_data='add_post_tokens')]
    rub_post = [InlineKeyboardButton(text='Разместить пост за рубли',
                                     callback_data='add_post_money')]
    help_but = [InlineKeyboardButton(text='Написать менеджеру', url=manager_tg)]
    back_but = [InlineKeyboardButton(text='⬅️ В меню', callback_data='back_to_menu')]
    keyboard_inline = [
            free_post,
            coins_post,
            # tokens_post,
            rub_post,
            help_but,
            back_but
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_inline)
    return keyboard


async def marketpalce_choice():
    wb = [KeyboardButton(text="WB")]
    ozon = [KeyboardButton(text="OZON")]
    keyboard = ReplyKeyboardMarkup(keyboard=[
            wb,
            ozon,
    ], resize_keyboard=True)
    return keyboard


async def channel_choice():
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=value,
                                                   callback_data=f'channel:{key}')] for key, value in
                             channels.items()])
    return keyboard


async def finish_public():
    public = [InlineKeyboardButton(text='Опубликовать', callback_data='finish_public')]
    menu = [InlineKeyboardButton(text='⬅️ Начать заново', callback_data='public')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            public,
            menu
    ])
    return keyboard


async def url_post_keyboard(url):
    button = [InlineKeyboardButton(text='Посмотреть товар',
                                   url=url)]
    return InlineKeyboardMarkup(inline_keyboard=[button])


async def search_keyboard():
    list_search = [InlineKeyboardButton(text='📋Список товаров в листе ожидания',
                                        callback_data='list_search')]
    add_product = [InlineKeyboardButton(text='➕Добавить товар в лист ожидания', callback_data='search')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            list_search,
            add_product
    ])
    return keyboard


async def delete_search_keyboard(id_search):
    button = [InlineKeyboardButton(text='Удалить', callback_data=f'del_search_{id_search}')]
    search_menu = [InlineKeyboardButton(text='Назад в меню',
                                            callback_data=f'back_to_menu')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            button,
            search_menu
    ])
    return keyboard


async def post_keyboard(post_id, active: bool) -> InlineKeyboardMarkup:
    post_deactivate = [InlineKeyboardButton(text='Снять с публикации',
                                            callback_data=f'my-post_deactivate_{post_id}')]
    post_public = [InlineKeyboardButton(text='Опубликовать', callback_data=f'public_again_{post_id}')]
    post_delete = [InlineKeyboardButton(text='Удалить пост навсегда',
                                        callback_data=f'my-post_delete_{post_id}')]
    if active:
        buttons = [post_deactivate, post_delete]
    else:
        buttons = [post_public, post_delete]
    post_menu = [InlineKeyboardButton(text='Назад в меню',
                                            callback_data=f'back_to_menu')]
    buttons.append(post_menu)
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def my_post_public_keyboard(id_post: int):
    """
    Функция создаёт кнопки для размещения постов в группе
    :return: InlineKeyboardMarkup
    """
    free_post = [InlineKeyboardButton(text='Опубликовать бесплатно',
                                      callback_data=f'again_free_{id_post}')]
    coins_post = [InlineKeyboardButton(text='Опубликовать за монеты 10 000 монет',
                                       callback_data=f'again_coins_{id_post}')]
    # tokens_post = [InlineKeyboardButton(text='Разместить пост за токены',
    #                                     callback_data='add_post_tokens')]
    rub_post = [InlineKeyboardButton(text='Опубликовать за рубли',
                                     callback_data=f'again_money_{id_post}')]
    back_but = [InlineKeyboardButton(text='⬅️ В меню', callback_data='back_to_menu')]
    keyboard_inline = [
            free_post,
            coins_post,
            # tokens_post,
            rub_post,
            back_but
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_inline)
    return keyboard


async def username_keyboard(username: str) -> ReplyKeyboardMarkup:
    back_button = [KeyboardButton(text="В меню")]
    name_insert_button = [KeyboardButton(text=username)]
    keyboard = ReplyKeyboardMarkup(keyboard=[
            name_insert_button,
            back_button
    ], resize_keyboard=True, is_persistent=True, one_time_keyboard=False)
    return keyboard


async def search_keyboard_delete() -> InlineKeyboardMarkup:
    menu_button = [InlineKeyboardButton(text="В меню", callback_data="back_to_menu")]
    back_button = [InlineKeyboardButton(text="Назад", callback_data="products_search")]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            back_button,
            menu_button
    ])
    return keyboard


async def delete_message_keyboard(id_message):
    button_delete = [InlineKeyboardButton(text="Да", callback_data=f"message_del_{id_message}")]
    menu_button = [InlineKeyboardButton(text="В меню", callback_data="back_to_menu")]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            button_delete,
            menu_button
    ])
    return keyboard


menu_button = [InlineKeyboardButton(text="В меню", callback_data="back_to_menu")]
back_menu_user = InlineKeyboardMarkup(inline_keyboard=[
        menu_button
])
