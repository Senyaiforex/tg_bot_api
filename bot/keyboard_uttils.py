from re import search

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo)

group_url = 'https://t.me/Buyer_Marketplace'
manager_tg = 'https://t.me/Broker_113'


async def start_keyboard():
    start_but = [InlineKeyboardButton(text='Подписаться', url=group_url)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[start_but])
    return keyboard

async def menu_keyboard(url: str):
    """
    Функция создаёт кнопки для меню
    :param url: str
    :return: InlineKeyboardMarkup
    """
    post = [InlineKeyboardButton(text='📥 Разместить пост в группе',
                                 callback_data='public')]
    catalog = [InlineKeyboardButton(text='📂 Каталог с товаром',
                                    callback_data='catalog')]
    search_prod = [InlineKeyboardButton(text='🔍 Поиск товара', callback_data='search')]
    group = [InlineKeyboardButton(text='👥 Группа', url=group_url)]
    webapp = [InlineKeyboardButton(text='Приложение',
                                   web_app=WebAppInfo(url=url))]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[post, catalog, search_prod, group, webapp])
    return keyboard


async def catalog_keyboard():
    """
    Функция создаёт кнопки для каталога с товарами
    :return: InlineKeyboardMarkup
    """
    catalog_list = [
            ('🎁БЕСПЛАТНО', 'https://t.me/+Nds62Ul98ToxNmYy'),
            ('Все категории', 'https://t.me/+yjKUe6sgZv80ZjYy'),
            ('Для женщин', 'https://t.me/+zWtFi86Nmro5Njcy'),
            ('Для мужчин', 'https://t.me/+VKcsGWuuIiAyZjli'),
            ('Автотовары', 'https://t.me/+i-ogg7MaSAo2MWQy'),
            ('Аптека', 'https://t.me/+25Sxw_4D6sZkYzVi'),
            ('Дом, мебель и ремонт', 'https://t.me/+VDDANitpLQ5hOTM6'),
            ('Зоотовары', 'https://t.me/+XHpYffckezFkOGZi'),
            ('Красота', 'https://t.me/+8GLEPn3HjH0yYTgy'),
            ('Продукты питания', 'https://t.me/+HiK1hczH70M5YWUy'),
            ('Дача', 'https://t.me/+zbC3WxB4VK9kNWM6'),
            ('Спорт', 'https://t.me/+CkRp9bCpnYA5OGZi'),
            ('Творчество', 'https://t.me/+A4k8LrMNcQg0NTU6'),
            ('Для взрослых', 'https://t.me/+vaqUJhHRrmA2Y2Y6'),
            ('Для детей', 'https://t.me/+sc4iUjURSAxjYjky'),
            ('Туризм, охота и рыбалка', 'https://t.me/+ghzZBQ-df3c1ZDEy'),
            ('Школа, книги и канцелярия', 'https://t.me/+Vwyw-rka09E0NzQ6'),
            ('Электротовары', 'https://t.me/+K97TaFqxqShmZTI6'),
            ('Украшения', 'https://t.me/+wO_SGsGwW5kwOThi'),

    ]
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
    coins_post = [InlineKeyboardButton(text='Разместить пост за монеты',
                                      callback_data='add_post_coins')]
    tokens_post = [InlineKeyboardButton(text='Разместить пост за токены',
                                      callback_data='add_post_tokens')]
    rub_post = [InlineKeyboardButton(text='Разместить пост за рубли',
                                      callback_data='add_post_tokens')]
    help_but = [InlineKeyboardButton(text='Написать менеджеру', url=manager_tg)]
    back_but = [InlineKeyboardButton(text='⬅️ В меню', callback_data='back_to_menu')]
    keyboard_inline = [
            free_post,
            coins_post,
            tokens_post,
            rub_post,
            help_but,
            back_but
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_inline)
    return keyboard

async def marketpalce_choice():
    wb = [KeyboardButton(text="WB")]
    ozon = [KeyboardButton(text="OZON")]
    skip = [KeyboardButton(text="Пропустить")]
    keyboard = ReplyKeyboardMarkup(keyboard=[
            wb,
            ozon,
            skip
    ])
    return keyboard

async def channel_choice():
    buyer = [InlineKeyboardButton(text='Buyer_Marketplace', callback_data='buyer')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buyer])
    return keyboard


async def finish_public():
    public = [InlineKeyboardButton(text='Опубликовать', callback_data='finish_public')]
    menu = [InlineKeyboardButton(text='⬅️ Начать заново', callback_data='public')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            public,
            menu
    ])
    return keyboard

