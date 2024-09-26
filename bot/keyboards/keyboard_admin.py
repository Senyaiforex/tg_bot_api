from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton,
                           InlineKeyboardMarkup)


async def menu_admin(superuser: bool):
    """
    Функция создаёт кнопки для меню Администратора
    :param superuser: bool
    :return: ReplyKeyboardMarkup
    """
    menu_buttons = [
            [KeyboardButton(text='🗒Добавить задание'),
             KeyboardButton(text='➖Удалить задание')],
            [KeyboardButton(text='➕Добавить пост'),
             KeyboardButton(text='🗑Удалить пост')],
            [KeyboardButton(text='📉Статистика'),
             KeyboardButton(text='🚫Блокировать')],
    ]
    if superuser:
        menu_buttons.append([KeyboardButton(text='👥Добавить администратора'),
                             KeyboardButton(text='💰Пул')])
        menu_buttons.append([KeyboardButton(text='💵Банк монет'),
                             KeyboardButton(text='📔Ликвидность на публикации')])
    keyboard = ReplyKeyboardMarkup(
            keyboard=menu_buttons, is_persistent=True,
            one_time_keyboard=False, resize_keyboard=True
    )
    return keyboard


async def inline_statistics() -> InlineKeyboardMarkup:
    """
    Создаёт inline кнопки для просмотра статистики
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Статистика по всем пользователям', callback_data='all_info_users'),
             InlineKeyboardButton(text='Информация о пользователе', callback_data='info_user')],
            [InlineKeyboardButton(text='Статистика по постам и заданиям', callback_data='info_posts')],
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def user_info_keyboard(telegram_id) -> InlineKeyboardMarkup:
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


async def pull_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт кнопку для создания пула
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Установить пул', callback_data='set_pull')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def select_type_task() -> InlineKeyboardMarkup:
    """
    Создаёт inline кнопки для создания задания
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Подписка на канал(группу)', callback_data='task_subscribe'),
             InlineKeyboardButton(text='Просмотр видео', callback_data='task_watch')],
            [InlineKeyboardButton(text='Поставить лайк', callback_data='task_like'),
             InlineKeyboardButton(text='Добавить в избранное', callback_data='task_save')],
            [InlineKeyboardButton(text='Оставить комментарий', callback_data='task_comment'),
             InlineKeyboardButton(text='Бонусы', callback_data='task_bonus')],
            [InlineKeyboardButton(text='Игра', callback_data='task_games')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def pull_inline() -> InlineKeyboardMarkup:
    """
    Создаёт inline кнопки для создания задания
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Посмотреть текущий пул', callback_data='current_pull')],
            [InlineKeyboardButton(text='Установить пул', callback_data='set_pull')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def menu_pull_confirm() -> InlineKeyboardMarkup:
    """
    Создаёт inline кнопки для подтверждения изменения пула
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Да', callback_data='confirm_pull'),
             InlineKeyboardButton(text='Нет', callback_data='set_pull')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def liquid_posts_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт inline кнопку для администратора для изменения
    пула ликвидности
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Изменить пул ликвидности', callback_data='set_liquid')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def menu_liquid_confirm() -> InlineKeyboardMarkup:
    """
    Создаёт inline кнопки для подтверждения изменения ликвидности
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Да', callback_data='confirm_liquid'),
             InlineKeyboardButton(text='Нет', callback_data='set_liquid')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


back_button = [KeyboardButton(text="Вернуться")]
back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                    keyboard=[back_button])
