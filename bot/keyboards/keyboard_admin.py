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
        menu_buttons.append([KeyboardButton(text='👥Добавить администратора')])
        menu_buttons.append([KeyboardButton(text='💰Пул')])
    keyboard = ReplyKeyboardMarkup(
            keyboard=menu_buttons,
    )
    return keyboard


async def inline_statistics():
    """
    Создаёт inline кнопки для просмотра статистики
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Все пользователи', callback_data='all_info_users'),
             InlineKeyboardButton(text='Информация о пользователе', callback_data='info_user')],
            [InlineKeyboardButton(text='Транзакции пользователя', callback_data='transactions_user'),
             InlineKeyboardButton(text='Статистика по постам', callback_data='info_posts')],
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
