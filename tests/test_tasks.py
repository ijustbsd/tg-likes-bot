from freezegun import freeze_time

from app import factories, models, tasks
from app.config.settings import settings


async def test_send_monthly_rating_task():
    user1 = factories.TelegramUserFactory(first_name="Иван", last_name="Иванов")
    await user1.save()
    user2 = factories.TelegramUserFactory(first_name="Петр", last_name="Петров")
    await user2.save()
    photo1 = factories.PhotoFactory(author=user1, likes=17, dislikes=-7, created_at="2023-02-17")
    await photo1.save()
    photo2 = factories.PhotoFactory(author=user1, likes=5, dislikes=-9, created_at="2023-02-01")
    await photo2.save()
    photo3 = factories.PhotoFactory(author=user2, likes=43, dislikes=-1, created_at="2023-02-28")
    await photo3.save()
    photo4 = factories.PhotoFactory(author=user2, likes=99, dislikes=-10, created_at="2023-03-01")
    await photo4.save()

    assert await models.Notification.all().count() == 0

    with freeze_time("2023-02-27 12:34:56"):
        await tasks.send_monthly_rating()

    assert await models.Notification.all().count() == 0

    with freeze_time("2023-02-28 12:34:56"):
        await tasks.send_monthly_rating()

    text = "\n".join(
        [
            "Февраль подходит к концу. Рейтинг за февраль:",
            "Петр Петров: 42",
            "Иван Иванов: 6",
        ]
    )
    notification = await models.Notification.get()
    assert notification.type == models.NotificationType.MONTHLY_RATING
    assert notification.text == text
    assert notification.parameters == {"year": 2023, "month": 2}
    assert notification.sent_at is None

    with freeze_time("2023-02-28 13:17:19"):
        await tasks.send_monthly_rating()

    assert await models.Notification.all().count() == 1

    with freeze_time("2023-03-01 12:34:56"):
        await tasks.send_monthly_rating()

    assert await models.Notification.all().count() == 1


async def test_send_daily_reminder_task():
    # TODO:
    assert True


async def test_send_notifications(mocker):
    settings.TG_CHAT_ID = -1234
    send_message_mock = mocker.patch("app.config.bot.bot.send_message")

    assert await models.Notification.all().count() == 0
    await tasks.send_notifications()
    send_message_mock.assert_not_called()

    await factories.NotificationFactory(sent_at="2022-09-01").save()
    await tasks.send_notifications()
    send_message_mock.assert_not_called()

    notification = factories.NotificationFactory(text="Привет!", sent_at=None)
    await notification.save()
    await tasks.send_notifications()
    send_message_mock.assert_called_with(-1234, "Привет!", parse_mode="Markdown")
    await notification.refresh_from_db()
    assert notification.sent_at is not None

    send_message_mock.reset_mock()
    await tasks.send_notifications()
    send_message_mock.assert_not_called()


async def test_send_notifications__error(mocker):
    settings.TG_CHAT_ID = -1234
    mocker.patch("app.config.bot.bot.send_message", side_effect=[RuntimeError, None])
    notification = factories.NotificationFactory(sent_at=None)
    await notification.save()

    await tasks.send_notifications()

    await notification.refresh_from_db()
    assert notification.sent_at is None

    await tasks.send_notifications()

    await notification.refresh_from_db()
    assert notification.sent_at is not None
