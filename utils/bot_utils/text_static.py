from dataclasses import dataclass
import os
BOT_USER_ID = os.getenv("BOT_FOR_USER")
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

channels = {
        # -1002409284453_237 для разработки в товары бесплатно
        # -1002409284453_29 для разработки во все категории
        # -1002409284453_2 для разработки для женщин
        '-1002090610085_325': 'Товары бесплатно',
        '-1002090610085_12955': 'Все категории',
        '-1002090610085_240': 'Для женщин',
        '-1002090610085_237': 'Для мужчин',
        '-1002090610085_194': 'Автотовары',
        '-1002090610085_192': 'Аптека',
        '-1002090610085_190': 'Дом, мебель и ремонт',
        '-1002090610085_242': 'Зоотовары',
        '-1002090610085_248': 'Красота',
        '-1002090610085_250': 'Продукты питания',
        '-1002090610085_260': 'Дача',
        '-1002090610085_252': 'Спорт',
        '-1002090610085_254': 'Творчество',
        '-1002090610085_256': 'Для взрослых',
        '-1002090610085_246': 'Для детей',
        '-1002090610085_315': 'Туризм, охота и рыбалка',
        '-1002090610085_266': 'Школа, книги и канцелярия',
        '-1002090610085_233': 'Электротовары',
        '-1002090610085_262': 'Украшения'}


@dataclass(frozen=True)
class TextAdminData:
    message_for_admin: str = ("Здравствуйте, администратор!\n\n"
                              "*В этом боте Вам доступны следующие функции:*\n"
                              "🗒Добавить задание - Добавить новое задание\n"
                              "➖Удалить задание - Удалить задание\n"
                              "📉Статистика - Показать статистику\n"
                              "🗑Удалить пост - Удалить пост\n"
                              "🚫Блокировать - Заблокировать пользователя\n"
                              "✅Разблокировать - Разблокировать пользователя"
                              )

    message_superuser: str = ("Здравствуйте, администратор!\n\n"
                              "*В этом боте Вам доступны следующие функции:*\n"
                              "🗒Добавить задание - Добавить новое задание\n"
                              "➖Удалить задание - Удалить задание\n"
                              "📉Статистика - Показать статистику\n"
                              "🗑Удалить пост - Удалить пост\n"
                              "🚫Блокировать - Заблокировать пользователя\n"
                              "✅Разблокировать - Разблокировать пользователя\n"
                              "👥Добавить администратора - Добавить нового администратора\n"
                              "➖Удалить администратора - Удалить администратора\n"
                              "💰Пул наград - Задать пул для приложения\n"
                              "💵Банк монет - Посмотреть текущий банк монет приложения\n"
                              "📔Ликвидность на публикации - Посмотреть или изменить ликвидность на публикации\n"
                              "🔥Сжечь монеты - Сжечь выбранное количество монет из банка")
    message_no_access: str = ("Здравствуйте! У вас недостаточно прав для использования данного бота. \n"
                              f"Используйте бот {BOT_USER_ID}")
    post_statistic: str = ("*Общая статистика*\n"
                           "Количество подписчиков в группе - _\r{count_sbs}_\r\n"
                           "Количество активных заданий - _\r{count_tasks}_\r\n\n"
                           "*Статистика по постам*\n"
                           "Количество опубликованных за месяц - _\r{posts_month}_\r\n"
                           "Количество опубликованных постов за сегодня - _\r{posts_today}_\r\n")
    add_telegram: str = "Введите _\rТелеграм id_\r пользователя, которого хотите добавить в администраторы"
    text_pull: str = ('*Текущее состояние пулла:*\n\n'
                      '*Монеты*\n'
                      'Задан - _\r{coins}_\r. Текущий - _\r{current_coins}_\r\n'
                      '*Фарминг*\n'
                      'Задан - _\r{farming}_\r. Текущий - _\r{current_farming}_\r\n'
                      '*Друзья*\n'
                      'Задан - _\r{friends}_\r. Текущий - _\r{current_friends}_\r\n'
                      '*Задания*\n'
                      'Задан - _\r{task}_\r. Текущий - _\r{current_task}_\r\n'
                      '*Краудсорсинг*\n'
                      'Задан - _\r{plan}_\r. Текущий - _\r{current_plan}_\r\n')
    block_username: str = "Введите _\rникнейм_\r пользователя, которого хотите заблокировать"
    unlock_username: str = "Введите _\rникнейм_\r пользователя, которого хотите разблокировать"
    post_delete_url: str = "Отправьте _\rссылку_\r на сообщение из группы, которое хотите удалить"
    task_delete_url: str = "Отправьте _\rссылку_\r на задание, которое хотите удалить"
    farming: str = "Введите количество пула для фарминга:"
    task_description: str = "Введите описание задания"
    info_username: str = "Введите _\rникнейм_\r пользователя, о котором хотите узнать информацию"
    pull_set_success: str = "Установлен новый пулл!"
    user_empty_transaction: str = "У пользователя отсутствуют транзакции"
    user_transaction_info: str = "Дата: `{date}`, Сумма: _\r{summ}_\r, Описание: _\r{type_transaction}_\r\n"
    user_empty_friends: str = "У данного пользователя нет приглашённых друзей"
    user_friends_info: str = ("Никнейм: @{username}, "
                              "Уровень: _\r{level}_\r, "
                              "Ранг: _\r{rank}_\r "
                              "Дата регистрации: `{date}`\n")
    telegram_id_invalid: str = "_\rID телеграм_\rдолжен состоять только из цифр, попробуйте ещё раз"
    username_add: str = "Введите _\rникнейм_\r пользователя, которого хотите добавить в администраторы"
    username_delete_adm: str = "Введите _\rникнейм_\r пользователя, которого хотите удалить из администраторов"
    admin_add_success: str = "Пользователь @{name} добавлен в администраторы"
    task_add_url: str = "Отправьте _\rссылку_\r на задание в виде\n`https://example/product/one.com`"
    task_add_date: str = ("Введите _\rдату_\r, до которой действительно это"
                          " задание(Последний день включительно)!\nФормат ввода : `01.01.2024`")
    task_date_invalid: str = ("Введена не правильная дата, "
                              "до которой действительно это задание(Последний день включительно)!\n"
                              "Формат ввода : `01.01.2024`")
    task_add_success: str = "Новое задание добавлено!"
    user_username_invalid: str = "Пользователь с таким _\rникнеймом_\r не найден"
    user_block_success: str = "Пользователь @{username} заблокирован!"
    user_unlock_success: str = "Пользователь @{username} разблокирован!"
    bank_text: str = "Общий банк монет составляет *{amount}* монет"
    task_expired: str = "Задание [{name}]({url}) удалено в связи с тем, что срок его размещения истёк"
    text_liquid: str = ("*Пул ликвидности постов за месяц*\n\n"
                        "*Постов бесплатно* \n"
                        "Необходимо - _\r{need_free}_\r.  На данный момент - _\r{current_free}_\r\n"
                        "*Постов за монеты*\n"
                        "Необходимо -  _\r{need_coins}_\r.  На данный момент - _\r{current_coins}_\r\n"
                        "*Постов за токены*\n"
                        "Необходимо - _\r{need_token}_\r.  На данный момент - _\r{current_token}_\r\n"
                        "*Постов за рубли*\n"
                        "Необходимо - _\r{need_money}_\r.  На данный момент - _\r{current_money}_\r\n"
                        "*Постов за звёзды*\n"
                        "Необходимо - _\r{need_stars}_\r.  На данный момент - _\r{current_stars}_\r")
    free: str = ("Введите требуемое количество публикуемых постов _\rбесплатно_\r. "
                 "Оно должно быть больше нуля")
    token: str = ("Введите требуемое количество публикуемых постов за _\rтокены_\r. "
                  "Оно должно быть больше нуля")
    coins: str = ("Введите требуемое количество публикуемых постов за _\rмонеты_\r. "
                  "Оно должно быть больше нуля")
    money: str = ("Введите требуемое количество публикуемых постов за _\rрубли_\r. "
                  "Оно должно быть больше нуля")
    liquid_invalid = ("Неверное значение параметра!\n"
                      "Пожалуйста, исправьте его и попробуйте заново, либо вернитесь "
                      "в главное меню нажав на /start")
    liquid_input_success: str = ("Установлен новое значение на {key}.\n"
                                 "Размер - {size}.\n"
                                 "*Теперь введите значение для {next_key}*")
    liquid_empty: str = ("Пожалуйста, введите правильные значения ликвидности всех остальных "
                         "составляющих(бесплатно, за токены, за монеты). Для этого"
                         "нажмите \start и начините заново")
    liquid_new_success: str = ("Посты бесплатно - _\r{free}_\r\n"
                               "Посты за токены - _\r{token}_\r\n"
                               "Посты за монеты - _\r{coins}_\r\n"
                               "Посты за рубли - _\r{money}_\r\n"
                               "Посты за звёзды - _\r{stars}_\r\n"
                               "Вы хотите установить новый пул ликвидности на публикации?")
    reward_input = "Введите сумму награды за выполнение задания"
    reward_invalid = ("Награда должна быть числом и не должна быть меньше или равна нулю.\n"
                      "Попробуйте ещё раз. Вводите награду без пробелов и знаков препинания")


@dataclass(frozen=True)
class TextUserData:
    no_subscribe: str = ("Добро пожаловать!\n"
                         "Чтобы пользоваться данным ботом необходимо подписаться на канал: @Buyer_Marketplace\n"
                         "После подписки снова нажмите /start")
    block: str = "Вы заблокированы администратором"
    name_product: str = ("Введите название товара\n"
                         "От 4 до 75 символов, без эмоджи-смайлов и специальных символов")
    name_invalid: str = ("Длина названия должна быть "
                         "от 4 до 75 символов, без эмоджи-смайлов и специальных символов. "
                         "Отправьте сообщение ещё раз.")
    cooperation: str = "Выберите способ размещения поста"
    search = ("Тут вы можете добавить нужный вам товар, когда он появится в продаже "
              "со скидкой, мы отправим вам сообщение в телеграмм!\n"
              "Название не должно иметь эмоджи-смайлов и спецсимволов\n"
              "Пример: Юбка")
    positive = ("✅ Отлично, добавили подписку на _\r{name}_\r\n"
                "Когда опубликуется, Вам придёт уведомление.")
    negative = (f"✖️ В вашем листе ожидания уже имеется 3 товара\n"
                f"Удалите товары из листа ожидания, и попробуйте заново")
    save_name = ("Название товара успешно сохранено! "
                 "Теперь загрузите фото товара.\n\n"
                 "_\rОбратите внимание, что размер фотографии "
                 "не должен превышать 1.5 МБ_\r")
    save_photo = ("Фото товара _\r'{product_name}'_\r успешно сохранено! "
                  f"Теперь укажите стоимость товара на маркетплейсе в данный момент\n")
    photo_cancell = ("Размер фотографии не должен превышать 1.5 МБ!\n"
                     f"Попробуйте ещё раз или нажмите кнопку /start")

    photo_error = "Пожалуйста, отправьте _\rфотографию товара_\r."
    discount_price = ("Укажите стоимость товара со скидкой(Кэшбеком).\n\n"
                      "Скидка должна быть "
                      "реальная и отличаться от стоимости "
                      "на маркетплейсе минимум на 15%\n"
                      "Введите стоимость без пробелов и знаков препинания")
    marketplace = "Выберите, на каком маркетплейсе будет покупка"

    url_acc = ("Укажите никнейм телеграм аккаунта, которому будут "
               "писать покупатели, переходящие по "
               "кнопке 'узнать условия'\n\n"
               "Никнейм аккаунта - Имя пользователя телеграмм аккаунта без символа '@'"
               )
    channel = "❗️Выберите необходимый канал для публикации"
    channel_success = "💢 Выбран канал для публикации - *{name}*"
    post_success = ("Успешно! Ваше объявление опубликовано!\n"
                    "Ссылка на Ваше объявление - [перейти]({url})")
    post_ready = ("🌟Объявление готово для публикации!\n\n"
                  "Обязательно проверьте правильность заполненных полей и ссылок!\n\n"
                  "Для окончания публикации нажмите кнопку ниже!")
    post_payment = ("Для публикации поста внесите оплату в размере _\r1000_\r рублей\n"
                    "Для оплаты, нажмите на [ссылку]({url})\n"
                    "После удачной оплаты мы разместим Ваш пост и оповестим Вас об этом")
    public_user = ("Ваше объявление:\n"
                   "Товар: {name}\n"
                   "Кэшбек: {value} р. ({discount}%)\n"
                   "Цена: {price} р.\n"
                   "Маркетплейс: {marketplace}\n"
                   "Цена для вас: {price_discount} р.\n"
                   "Аккаунт для связи: {url}")
    post = (
            "⭐️{name}⭐️\n\n"
            "💵Кэшбек: {value} р. ({discount}%)\n\n"
            "💵Цена на {marketplace}: {price} р.\n"
            "💵Цена для вас: {price_discount} р.\n\n\n"
            "🤝 Согласовать выкуп с @{url}")
    post_invalid = ("Неправильное содержание поста!\n"
                    "Посмотрите примеры публикаций "
                    "в нашей [группе](https://t.me/Buyer_Marketplace)")
    not_coins = ("У вас на счету недостаточно монет!\n"
                 "Для публикации поста необходимо 10 000 монет\n"
                 "Выполняйте задания в приложении и приглашайте друзей для "
                 "увеличения количества монет")
    info_search = ("Здесь Вам доступны следующие действия:\n\n"
                   "1.Список названий товаров в листе ожидания\n"
                   "2.Добавить новые названия в лист ожидания\n"
                   "3.Удалить те товары, которые Вам не нужны.\n\n"
                   "Максимальное количество товаров в листе ожидания - 3")
    info_post = ("Ваше объявление:\n"
                 "Товар: {name}\n"
                 "Кэшбек: {value} р. ({discount}%)\n"
                 "Цена: {price} р.\n"
                 "Цена для вас: {price_discount} р.\n"
                 "Аккаунт для связи: @{url}")
    post_expired = ("Ваше [объявление]({url}) удалено, так как истёк срок его размещения.\n "
                    "Для его продления Вам необходимо будет перейти во вкладку "
                    "'Мои объявления' и опубликовать его заново, "
                    "либо создать новое объявление и опубликовать его ")


txt_adm = TextAdminData()
txt_us = TextUserData()

dict_text = {"free": "Вы выбрали *бесплатное* размещение поста\n\n"
                     + txt_us.name_product,
             "money": "Вы выбрали размещение поста за рубли. Стоимость - *1000 р.*\n\n"
                      + txt_us.name_product,
             "coins": "Вы выбрали размещение поста за монеты. Стоимость - *10000 монет*\n\n"
                      + txt_us.name_product,
             "stars": "Вы выбрали размещение поста за звёзды. Стоимость - *500 звёзд*\n\n"
                      + txt_us.name_product
             }
