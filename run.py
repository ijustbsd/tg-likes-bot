import asyncio

from aiogram import Bot

from app.config.bot import bot
from app.db import close
from app.db import init
from app.dispatcher import dp


async def on_startup(bot: Bot):
    await init()


async def on_shutdown(bot: Bot):
    await close()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
