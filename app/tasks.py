import datetime as dt
import logging
from collections import defaultdict

from tortoise import transactions

from app.helpers import month_number_to_name
from app.models import Notification
from app.models import NotificationType
from app.models import Photo


async def send_monthly_rating() -> None:
    today: dt.date = dt.datetime.utcnow().date()
    tomorrows_month: int = (today + dt.timedelta(days=1)).month
    if today.month == tomorrows_month:
        return
    if await Notification.filter(
        type=NotificationType.MONTHLY_RATING,
        parameters__contains={"year": today.year, "month": today.month},
    ).exists():
        return
    month_name = month_number_to_name(today.month)
    text = f"{month_name.capitalize()} подходит к концу. Рейтинг за {month_name}:\n"
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
    await Notification.create(
        type=NotificationType.MONTHLY_RATING,
        text=text,
        parameters={"year": today.year, "month": today.month},
    )


async def send_daily_reminder() -> None:
    now = dt.datetime.utcnow().astimezone(tz=dt.UTC)
    last_photo = await Photo.filter().order_by("-created_at").first()
    if last_photo is None:
        return

    if last_photo.created_at > now - dt.timedelta(days=1):
        return

    if await Notification.filter(
        type=NotificationType.DAILY_REMINDER,
        parameters__contains={"last_photo_id": last_photo.id},
    ).exists():
        return

    await Notification.create(
        type=NotificationType.DAILY_REMINDER,
        text="Эх... Давно картиночек не было 🥲",
        parameters={"last_photo_id": last_photo.id},
    )


async def send_notifications() -> None:
    not_sent_notifications = await Notification.filter(sent_at__isnull=True)
    for n in not_sent_notifications:
        async with transactions.in_transaction():
            notification = await Notification.select_for_update(skip_locked=True).get_or_none(id=n.id)  # type: ignore
            if notification is None or notification.sent_at is not None:
                continue
            try:
                await notification.send()
            except Exception:
                logging.exception(f"Ошибка при отправке уведомления! ({notification.id=})")
                continue
