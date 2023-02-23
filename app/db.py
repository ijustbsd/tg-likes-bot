from tortoise import Tortoise

from .config import settings


async def init() -> None:
    await Tortoise.init(settings.TORTOISE_ORM)


async def close() -> None:
    await Tortoise.close_connections()
