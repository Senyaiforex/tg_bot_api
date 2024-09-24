from datetime import datetime, timedelta
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_tasks(session: AsyncSession):
    """
    Функция для добавлений тестовых заданий в базу данных
    """
    from models import CategoryTask, Task
    result = await session.execute(select(Task).limit(1))
    tasks_exists = result.scalar_one_or_none()
    if tasks_exists:  # задания уже есть в БД
        return
    categories = [1, 2, 3, 4, 5, 6, 7]
    urls_tasks = [('https://t.me/EFT_Russia_chat', 'Подписаться на чат психологов'),
                  ('https://t.me/dpdg_emdr_free', 'Подписаться на ДМПТ'),
                  ('https://t.me/Buyer_Marketplace', 'Подписаться на BUYER'),
                  ('https://t.me/liberty_404', 'Подписатсья на LIBERTI'),
                  ('https://t.me/m_worker_open', 'Подписаться на поиск работы'),
                  ('https://t.me/clubdvizh', 'Подписаться на КЛУБНЫЙ ДВИЖ')]
    for i in range(len(urls_tasks)):
        task_entry = Task(category_id=1,
                          description=urls_tasks[i][1],
                          url=urls_tasks[i][0],
                          date_limit=datetime.now().today().date() + timedelta(days=random.randint(30, 80)))
        session.add(task_entry)
    urls_games = [('https://t.me/empirebot', 'Играть в X-EMPIRE BOT'),
                  ('https://t.me/PokerBot', 'Играть в ПОКЕР'),
                  ('https://t.me/g01snake_bot', 'Игра змейка в телеграм'),
                  ('https://t.me/ChessBot', 'Первые шахматы в телеграм'),
                  ('https://telegram.me/mytetrisbot', 'Лучший тетрис')]
    for j in range(len(urls_games)):
        task_entry = Task(category_id=2,
                          description=urls_games[j][1],
                          url=urls_games[j][0],
                          date_limit=datetime.now().today().date() + timedelta(days=random.randint(30, 80)))
        session.add(task_entry)
    urls_videos = [('https://www.youtube.com/watch?v=FfitVqUAVl8', 'Лучшее видео про PYTHON'),
                   ('https://www.youtube.com/watch?v=bQpfvz1bIoE', 'Планировка задач REDIS'),
                   ('https://youtu.be/Gp0a_rBlbE0?si=IztrEn94HIev_sPy', 'Как лечить спазмы в мышцах'),
                   ('https://youtu.be/Y0qKYFZDlmo?si=3rFyt89cnu0yZ35c', 'SEO оптимизация сайта')]
    for k in range(len(urls_videos)):
        task_entry = Task(category_id=3,
                          description=urls_videos[k][1],
                          url=urls_videos[k][0],
                          date_limit=datetime.now().today().date() + timedelta(days=random.randint(30, 80)))
        session.add(task_entry)

    urls_likes = [('https://vk.com/wall-212808533_4226079', 'Лайк на пост ВК'),
                  ('https://vk.com/wall-30111136_2662747', 'Поставить лайк на комментарий'),
                  ('https://vk.com/wall-26750264_1970271', 'Поставить лайк на фотографии'),
                  ('https://vk.com/wall-26750264_1970240', 'Лайк на описание фильма')]
    for z in range(len(urls_likes)):
        task_entry = Task(category_id=4,
                          description=urls_likes[z][1],
                          url=urls_likes[z][0],
                          date_limit=datetime.now().today().date() + timedelta(days=random.randint(30, 80)))
        session.add(task_entry)
    urls_comment = [('https://vk.com/wall-212808533_4226079', 'Прокомментировать пост вконтакте'),
                  ('https://vk.com/wall-30111136_2662747', 'Комментарий к фильму'),
                  ('https://vk.com/wall-26750264_1970271', 'Комментарий к фотографии'),
                  ('https://vk.com/wall-26750264_1970240', 'Комментарий к посту')]
    for y in range(len(urls_comment)):
        task_entry = Task(category_id=5,
                          description=urls_comment[y][1],
                          url=urls_comment[y][0],
                          date_limit=datetime.now().today().date() + timedelta(days=random.randint(30, 80)))
        session.add(task_entry)
    urls_save = [('https://www.ozon.ru/product/botinki-tervolina-1624668588/?campaignId=433', 'Товар в избранное на OZON'),
                  ('https://www.ozon.ru/product/timio-f152g-pro-noutbuk-15-6-intel-celeron-n5095-ram-8-gb-ssd-256-gb-intel-uhd-graphics-750-1685336651/?advert=AL0AuKbV5IrNemXIqU9qTHNEh6c1Ul70ETzFCmapHJ8WZgoFL9XnEmB8wcTtyqI4HtdZ-OFmrbXdPa0XLd46rRxKUJnS606rXncp4cTbpd1ZfAMkVY2TXHexiF0mIWiAbEXtwRW93ALlArjmWcNEMSXGHWEn1yZETrEsZYteo5m2iz5YDeglqWeeXGYKePKu9QuxmioT2LKLx3WgMjDC1kJf9hPMpUNrDCeN9OD9UTs2hKaMs5FSyq1K4UKTRWnreVSZNgRnWuwoKRNeEcb_WlXJwREuB5ESQn6BZueq7qF8RPAQ_VCjOw2_gbPw5J9hWVs6c-67ps76cYpPHdBm37tuGjO-Iwyakxs1RUc&avtc=1&avte=4&avts=1727216815', 'Добавить товар в избранное на OZON'),
                  ('https://www.ozon.ru/product/videonyanya-besprovodnaya-baby-monitor-s-kameroy-i-monitorom-1628779110/?advert=AL0AcqzRii9s9rqpcchybvmvxrniDrGsi4Sl7Vokjucv0DyOK86GxQ2s4XNzGfP9BFFW3dPJyoiqCEaAY2yuKv8Q6arb4AzAMgvjRy_z-oTvNWwyIe9tdDCSvegrUmMCFAv249ox8zvEQhQUm8Kb-PF7BvHpdI35BVD5I2jmom9NXXA10Fe2z9ht1gUSbqlyRDPuk7LIJ-zankKtALBKJNGHWfeJ00FFGQGbEpQuM2im8PYcF-am4R0BNpnVL9n6oNGRD2WQeIEQAKqc9g6UuSZCYRhf6TKZnlVpcKkwUYzt3lB7qSab7mVxszctVntATqaR4KZsVoMvMpyuFsYMklu6MkrYtLOV&avtc=1&avte=4&avts=1727216851', 'Добавить товар в избранное '),
                  ('https://www.wildberries.ru/catalog/181967824/detail.aspx', 'Товар на WILDBERRIES'),
                 ('https://www.wildberries.ru/catalog/155681557/detail.aspx', 'Добавить товар на WILBERRIES в избранное'),
                 ('https://www.wildberries.ru/catalog/247067172/detail.aspx', 'Добавить товар на WB в избранное')]
    for x in range(len(urls_save)):
        task_entry = Task(category_id=6,
                          description=urls_save[x][1],
                          url=urls_save[x][0],
                          date_limit=datetime.now().today().date() + timedelta(days=random.randint(30, 80)))
        session.add(task_entry)
    urls_bonus = [('https://t.me/EFT_Russia_chat', 'Подпишись и получи 3 спиннера'),
                  ('https://t.me/dpdg_emdr_free', 'Подпишись и получи 5000 монет'),
                  ('https://t.me/Buyer_Marketplace', 'Подпишись и получи 100 токенов'),
                  ('https://t.me/liberty_404', 'Подпишись и получи 1000 монет'),
                  ('https://t.me/m_worker_open', 'Подпишись и получи 1 спиннер'),
                  ('https://t.me/clubdvizh', 'Подпишись и получи 500 токенов')]
    for d in range(len(urls_bonus)):
        task_entry = Task(category_id=7,
                          description=urls_bonus[d][1],
                          url=urls_bonus[d][0],
                          date_limit=datetime.now().today().date() + timedelta(days=random.randint(30, 80)))
        session.add(task_entry)
    await session.commit()
