from repository import get_user_by_telegram_id, get_task_by_id, add_task
from bot.bot_main import bot


async def is_user_subscribed(user_id: int, channel_id: str) -> bool:
    member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    return member.status in ["member", "administrator", "creator"]


async def get_channel_id_by_url(url: str) -> str:
    channel_id = url.split("//")[-1].split("/")[1]
    return f'@{channel_id}'


async def check_task_complete(telegram_id: int, task_id: int, session) -> bool:
    user = await get_user_by_telegram_id(telegram_id, session)
    task = await get_task_by_id(task_id, session)
    if task.type_task == 'subscribe':
        if await is_user_subscribed(telegram_id, await get_channel_id_by_url(task.url)):
            await add_task(user, task, session)
            return True
    return False
