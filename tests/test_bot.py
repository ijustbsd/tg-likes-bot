import datetime as dt
from unittest.mock import ANY, AsyncMock

import pytest
from freezegun import freeze_time

from app import bot, factories, models, schemas


@pytest.fixture()
def user():
    return factories.TelegramUserFactory()


@pytest.fixture()
def message(user):
    message_mock = AsyncMock()
    message_mock.message_id = 7
    message_mock.chat.id = 42
    message_mock.from_user = user
    return message_mock


@pytest.fixture()
def callback_query(message):
    callback_query_mock = AsyncMock()
    callback_query_mock.id = 19
    callback_query_mock.from_user = message.from_user
    callback_query_mock.message = message
    return callback_query_mock


async def test_photo_handler__user_and_photo_created(message):
    assert await models.TelegramUser.all().count() == 0
    assert await models.Photo.all().count() == 0

    with freeze_time("2022-03-17 12:34:56"):
        await bot.photo_handler(message)

    user = await models.TelegramUser.get()
    assert user.username == message.from_user.username
    assert user.first_name == message.from_user.first_name
    assert user.last_name == message.from_user.last_name

    photo = await models.Photo.get().prefetch_related("author")
    assert photo.id == message.message_id
    assert photo.author == message.from_user
    assert photo.likes == 0
    assert photo.dislikes == 0
    assert photo.created_at == dt.datetime(2022, 3, 17, 12, 34, 56, tzinfo=dt.timezone.utc)


async def test_photo_handler__user_and_photo_already_exist(message):
    await message.from_user.save()
    await factories.PhotoFactory(id=message.message_id, author=message.from_user).save()
    assert await models.TelegramUser.all().count() == 1
    assert await models.Photo.all().count() == 1

    with freeze_time("2022-03-17 12:34:56"):
        await bot.photo_handler(message)

    assert await models.TelegramUser.all().count() == 1
    assert await models.Photo.all().count() == 1
    message.reply.assert_called_with("Тебе понравилась эта картинка?", reply_markup=ANY)


@pytest.mark.parametrize(
    ("action", "vote_value", "likes", "dislikes", "likes_excepted", "dislikes_excepted", "rating", "rating_excepted"),
    [
        (schemas.VoteActionEnum.UP, 1, 12, 10, 13, 10, 16, 17),
        (schemas.VoteActionEnum.DOWN, -1, 12, 10, 12, 9, 16, 15),
    ],
)
async def test_vote_callback_handler(
    mocker,
    callback_query,
    action,
    vote_value,
    likes,
    dislikes,
    likes_excepted,
    dislikes_excepted,
    rating,
    rating_excepted,
):
    answer_callback_query_mock = mocker.patch("app.bot.bot.answer_callback_query")
    edit_message_reply_markup_mock = mocker.patch("app.bot.bot.edit_message_reply_markup")
    await callback_query.from_user.save()
    author = factories.TelegramUserFactory(rating=rating)
    await author.save()
    photo = factories.PhotoFactory(
        author=author,
        likes=likes,
        dislikes=dislikes,
    )
    await photo.save()

    callback_data = {
        "message_id": photo.id,
        "action": action,
    }
    with freeze_time("2022-03-17 12:34:56"):
        await bot.vote_callback_handler(callback_query, callback_data)

    await photo.refresh_from_db()
    await author.refresh_from_db()
    assert photo.likes == likes_excepted
    assert photo.dislikes == dislikes_excepted
    assert author.rating == rating_excepted
    vote = await models.Vote.get().prefetch_related("user", "photo")
    assert vote.photo == photo
    assert vote.user == callback_query.from_user
    assert vote.value == vote_value
    edit_message_reply_markup_mock.assert_called_with(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=ANY,
    )
    answer_callback_query_mock.assert_called_with(callback_query.id, "Твой голос учтён!")


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

    await bot.rating_handler(message)

    text = "*Рейтинг участников:*\nСергей Бабошин: 17\nЕкатерина Тарасова: 14"
    send_message_mock.assert_called_with(42, text, parse_mode="Markdown")


async def test_rating_handler__empty_users(message):
    assert await models.TelegramUser.all().count() == 0
    await bot.rating_handler(message)
    message.reply.assert_called_with("Не найдено ни одного участника!")
