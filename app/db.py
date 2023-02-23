from aerich import Command
from tortoise import Tortoise

from .config import settings


async def init(create_db: bool = False) -> None:
    await Tortoise.init(settings.TORTOISE_ORM, _create_db=create_db)

    command = Command(tortoise_config=settings.TORTOISE_ORM, app="models")
    await command.init()
    await command.upgrade()


async def close() -> None:
    await Tortoise.close_connections()
