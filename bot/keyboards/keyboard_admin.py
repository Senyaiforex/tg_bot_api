from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo)


async def menu_admin(superuser: bool):
    """
    Функция создаёт кнопки для меню Администратора
    :param superuser: bool
    :return: ReplyKeyboardMarkup
    """
    menu_buttons = [
            [KeyboardButton(text='🗒Добавить задание'),
             KeyboardButton(text='📉Статистика')],
            [KeyboardButton(text='➕Добавить пост'),
             KeyboardButton(text='🗑Удалить пост')],
            [KeyboardButton(text='🚫Блокировать')],
    ]
    if superuser:
        menu_buttons[2].append(KeyboardButton(text='👥Добавить администратора'))
        menu_buttons.append([KeyboardButton(text='💰Пул')])
    keyboard = ReplyKeyboardMarkup(
            keyboard=menu_buttons, is_persistent=True
    )
    return keyboard


async def inline_statistics():
    """
    Создаёт inline кнопки для просмотра статистики
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Статистика по пользователям', callback_data='all_info_users'),
             InlineKeyboardButton(text='Информация о пользователе', callback_data='info_user')],
             [InlineKeyboardButton(text='Статистика по постам', callback_data='info_posts')],
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def user_info_keyboard(telegram_id):
    """
    Создаёт inline кнопки для просмотра статистики по отдельному пользователю
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Все транзакции', callback_data=f'transactions_{telegram_id}'),
             InlineKeyboardButton(text='Друзья', callback_data=f'friends_{telegram_id}')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard

async def pull_keyboard():
    """
    Создаёт кнопку для создания пула
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Установить пулл', callback_data='set_pull')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def select_type_task():
    """
    Создаёт inline кнопки для создания задания
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Подписка на канал(группу)', callback_data='task_subscribe'),
             InlineKeyboardButton(text='Просмотр видео', callback_data='task_watch')],
            [InlineKeyboardButton(text='Поставить лайк', callback_data='task_like'),
             InlineKeyboardButton(text='Добавить в избранное', callback_data='task_save')],
            [InlineKeyboardButton(text='Оставить комментарий', callback_data='task_comment')],
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def pull_inline():
    """
    Создаёт inline кнопки для создания задания
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Посмотреть текущий пул', callback_data='current_pull')],
            [InlineKeyboardButton(text='Установить пул', callback_data='install_pull')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard
