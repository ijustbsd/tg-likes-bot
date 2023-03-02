import asyncio
import datetime as dt
from collections import defaultdict

from aiogram import Bot
from celery import Celery, shared_task
from tortoise import transactions

from app.bot import bot
from app.config.celery import app as celery_app
from app.config.settings import settings
from app.helpers import month_number_to_name
from app.models import MonthlyRatingMessage, Photo


def setup_periodic_tasks(sender: Celery, **_):
    sender.add_periodic_task(3600, send_monthly_rating_task.s())


async def send_monthly_rating(bot: Bot):
    today: dt.date = dt.datetime.utcnow().date()
    tomorrows_month: int = (today + dt.timedelta(days=1)).month
    if today.month == tomorrows_month:
        return
    if await MonthlyRatingMessage.filter(year=today.year, month=today.month).exists():
        return
    month_name = month_number_to_name(today.month).capitalize()
    text = f"{month_name} подходит к концу. Текущий рейтинг участников:\n"
    photos = await Photo.filter(
        created_at__gte=today.replace(day=1),
        created_at__lte=today,
    ).prefetch_related("author")
    rating: defaultdict[str, int] = defaultdict(int)
    for photo in photos:
        rating[photo.author.name] += photo.likes + photo.dislikes
    if not rating:
        return
    rating_sorted = sorted(rating.items(), key=lambda x: x[1], reverse=True)
    text += "\n".join([f"{name}: {votes}" for name, votes in rating_sorted])
    async with transactions.in_transaction():
        await bot.send_message(settings.TG_CHAT_ID, text, parse_mode="Markdown")
        await MonthlyRatingMessage.create(year=today.year, month=today.month, message=text)


@shared_task
def send_monthly_rating_task():
    asyncio.run(send_monthly_rating(bot))


setup_periodic_tasks(celery_app)
