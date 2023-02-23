from unittest.mock import AsyncMock

import pytest

from app import factories, models
from app.bot import rating_handler


@pytest.fixture()
def message():
    message_mock = AsyncMock()
    message_mock.chat.id = 42
    return message_mock


async def test_rating_handler(mocker, message):
    send_message_mock = mocker.patch("app.bot.bot.send_message")
    await factories.TelegramUserFactory(
        first_name="Сергей",
        last_name="Бабошин",
        rating=17,
    ).save()
    await factories.TelegramUserFactory(
        first_name="Екатерина",
        last_name="Тарасова",
        rating=14,
    ).save()
    assert await models.TelegramUser.all().count() == 2

    await rating_handler(message)

    text = "*Рейтинг участников:*\nСергей Бабошин: 17\nЕкатерина Тарасова: 14"
    send_message_mock.assert_called_with(42, text, parse_mode="Markdown")


async def test_rating_handler__empty_users(message):
    assert await models.TelegramUser.all().count() == 0
    await rating_handler(message)
    message.reply.assert_called_with("Не найдено ни одного участника!")
