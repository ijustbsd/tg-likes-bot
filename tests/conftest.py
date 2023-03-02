import asyncio

import pytest
from tortoise import Tortoise

from app import db
from app.config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    settings.TORTOISE_ORM["connections"]["default"]["credentials"]["database"] = "test"
    await db.init(create_db=True)
    try:
        yield
    finally:
        await Tortoise._drop_databases()
        await db.close()


@pytest.fixture(autouse=True)
async def clear_tables():
    try:
        yield
    finally:
        for model in Tortoise.apps["models"].values():
            conn = Tortoise.get_connection("default")
            await conn.execute_query(f"DELETE FROM {model._meta.db_table}")
