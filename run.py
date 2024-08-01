import asyncio

from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web

from app.config.bot import bot
from app.config.settings import settings
from app.db import close
from app.db import init
from app.dispatcher import dp


async def on_startup(bot: Bot):
    await init()
    await bot.set_webhook(f"{settings.URL}/{settings.WEBHOOK_PATH}", secret_token=settings.WEBHOOK_SECRET)


async def on_shutdown(bot: Bot):
    await close()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    asyncio.run(main())
