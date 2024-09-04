from aiohttp import web
import asyncio
from bot_main import check_task_complete
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_task(request):
    telegram_id = request.match_info.get('telegram_id')
    task_id = request.match_info.get('task_id')
    complete = await check_task_complete(telegram_id, task_id)
    response_data = {'complete': complete}
    return web.json_response(response_data)

app = web.Application()
app.router.add_get('/check_task/{telegram_id}/{task_id}', check_task)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=8443)
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_web_server())
