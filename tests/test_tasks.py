from freezegun import freeze_time

from app import factories, models, tasks
from app.bot import bot
from app.config.settings import settings


async def test_send_monthly_rating_task(mocker):
    settings.TG_CHAT_ID = -1234
    send_message_mock = mocker.patch("app.bot.bot.send_message")
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

    assert await models.MonthlyRatingMessage.all().count() == 0

    with freeze_time("2023-02-27 12:34:56"):
        await tasks.send_monthly_rating(bot)

    send_message_mock.assert_not_called()
    assert await models.MonthlyRatingMessage.all().count() == 0

    with freeze_time("2023-02-28 12:34:56"):
        await tasks.send_monthly_rating(bot)

    text = "\n".join(
        [
            "Февраль подходит к концу. Текущий рейтинг участников:",
            "Петр Петров: 42",
            "Иван Иванов: 6",
        ]
    )
    send_message_mock.assert_called_with(-1234, text, parse_mode="Markdown")
    send_message_mock.reset_mock()
    assert await models.MonthlyRatingMessage.all().count() == 1
    assert await models.MonthlyRatingMessage.get_or_none(year=2023, month=2, message=text)

    with freeze_time("2023-03-01 12:34:56"):
        await tasks.send_monthly_rating(bot)

    send_message_mock.assert_not_called()
    assert await models.MonthlyRatingMessage.all().count() == 1
