import pytest

from app import factories


@pytest.mark.parametrize(
    ("user", "name"),
    [
        ({"username": "baboshin", "first_name": "Сергей", "last_name": "Бабошин"}, "Сергей Бабошин"),
        ({"username": "baboshin"}, "baboshin"),
        ({}, "42"),
    ],
)
async def test_telegram_user_name(user, name):
    user_data = {
        "id": 42,
        "username": "",
        "first_name": "",
        "last_name": "",
    }
    user_data.update(user)

    user = factories.TelegramUserFactory(**user_data)
    await user.save()

    assert user.name == name
