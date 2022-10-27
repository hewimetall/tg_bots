import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import MemoryStorage
from aiogram.utils import executor

from handler import text_handler, start_handler, info_handler, media_handler, \
    swith_handler, add_text_handler, finish_handler
from helper import MenuState
from settings import Setting

settings = Setting()

logging.basicConfig(level=logging.DEBUG)

API_TOKEN = settings.conf.defaults()['token']
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


# Init message
dp.message_handler(state=None)(start_handler)
# For start create news
dp.callback_query_handler(lambda c: c.data == "cmd_start", state=MenuState.START)(text_handler)
# For wait start create news
dp.message_handler(state=MenuState.START)(info_handler)
# Add media
dp.message_handler(state=MenuState.MEDIA, content_types=['photo', 'text', 'document'] )(media_handler)
# Route wait message send | add media | undo
dp.callback_query_handler(state=MenuState.TEXT)(swith_handler)
# Add text
dp.message_handler(state=MenuState.TEXT)(add_text_handler)
# Route wait message send and reload
dp.callback_query_handler(state=MenuState.FINISH)(finish_handler)

if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
