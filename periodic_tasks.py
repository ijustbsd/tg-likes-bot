import asyncio
import logging
from contextlib import suppress
from datetime import datetime
from typing import Any
from typing import Awaitable
from typing import Callable

from app import db
from app import tasks


async def worker(
    name: str,
    func: Callable[[], Awaitable[Any]],
    interval: int,
    delay: int,
) -> None:
    logging.info(
        "Starting task %s with interval %i seconds and delay %i seconds",
        name,
        interval,
        delay,
    )
    await asyncio.sleep(delay)
    while True:
        logging.info("Run task %s", name)
        t = datetime.utcnow()
        try:
            await func()
        except Exception as ex:
            logging.exception(ex)
        else:
            logging.info(
                "Done task %s in %i seconds and sleep for %i seconds",
                name,
                (datetime.utcnow() - t).total_seconds(),
                interval,
            )
        await asyncio.sleep(interval)


async def main() -> None:
    await db.init()
    await asyncio.gather(
        worker(
            "send_monthly_rating",
            tasks.send_monthly_rating,
            interval=3600,
            delay=10,
        ),
        worker(
            "send_daily_reminder",
            tasks.send_daily_reminder,
            interval=300,
            delay=10,
        ),
        worker(
            "send_notifications",
            tasks.send_notifications,
            interval=300,
            delay=10,
        ),
    )
    await db.close()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
