from aiogram import Dispatcher, executor

from app.bot import dp
from app.db import close, init


async def on_startup(_: Dispatcher):
    await init()


async def on_shutdown(_: Dispatcher):
    await close()


if __name__ == "__main__":
    bot_executor = executor.Executor(dp, skip_updates=True)
    bot_executor.on_startup(on_startup)
    bot_executor.on_shutdown(on_shutdown)
    bot_executor.start_polling()
