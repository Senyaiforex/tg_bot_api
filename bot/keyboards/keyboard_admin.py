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
             KeyboardButton(text='➖Удалить задание'),
             KeyboardButton(text='📉Статистика')],

            [KeyboardButton(text='🗑Удалить пост'),
             KeyboardButton(text='🚫Блокировать'),
             KeyboardButton(text='✅Разблокировать')],
    ]
    if superuser:
        menu_buttons.append([KeyboardButton(text='👥Добавить администратора'),
                             KeyboardButton(text='➖Удалить администратора'),
                             KeyboardButton(text='💰Пул наград')])

        menu_buttons.append([KeyboardButton(text='💵Банк монет'),  # 🔥
                             KeyboardButton(text='📔Ликвидность на публикации'),
                             KeyboardButton(text='🔥Сжечь монеты')])
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
            [InlineKeyboardButton(text='Бонусы', callback_data='task_bonus'),
             InlineKeyboardButton(text='Игра', callback_data='task_games')],
            [InlineKeyboardButton(text='Другие задания', callback_data='task_task')],
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


back_button = [KeyboardButton(text="⬅️ Назад")]
back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                    is_persistent=True,
                                    one_time_keyboard=False,
                                    keyboard=[back_button])


async def type_pulls_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для выбора типа пула для изменения
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Пул на монеты', callback_data='pull_coins')],
            [InlineKeyboardButton(text='Пул на друзей', callback_data='pull_friends')],
            [InlineKeyboardButton(text='Пул на фарминг', callback_data='pull_farming')],
            [InlineKeyboardButton(text='Пул на краудсорсинг', callback_data='pull_plan')],
            [InlineKeyboardButton(text='Пул на задания', callback_data='pull_tasks')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='menu')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def type_liquid_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт inline кнопки для администратора для изменения
    пула ликвидности
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Посты бесплатно', callback_data='liquid_free')],
            [InlineKeyboardButton(text='Посты за монеты', callback_data='liquid_coins')],
            [InlineKeyboardButton(text='Посты за рубли', callback_data='liquid_money')],
            [InlineKeyboardButton(text='Посты за токены', callback_data='liquid_token')],
            [InlineKeyboardButton(text='Посты за звёзды', callback_data='liquid_stars')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='menu')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def back_to_pull() -> InlineKeyboardMarkup:
    """
    Создаёт кнопку для возврата к меню пулов
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Назад', callback_data='info_pull')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard


async def remission_coins_keyboard(size: str) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для подтверждения сжигания монет
    :param size:
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Да', callback_data=f'confirm_remission_{size}'),
             InlineKeyboardButton(text='Назад', callback_data='menu')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons)
    return keyboard


back_menu_inline = [InlineKeyboardButton(text="Назад", callback_data="menu")]
back_menu = InlineKeyboardMarkup(inline_keyboard=[back_menu_inline])


async def back_to_liquid() -> InlineKeyboardMarkup:
    """
    Создаёт кнопку для возврата к меню ликвидности
    :return:
    """
    menu_inline_buttons = [
            [InlineKeyboardButton(text='Назад', callback_data='info_liquid')]
    ]
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=menu_inline_buttons,
    )
    return keyboard
