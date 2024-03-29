import datetime as dt
import logging

from aiogram import Dispatcher
from aiogram import types
from tortoise import exceptions
from tortoise import transactions

from app.config.bot import bot
from app.helpers import action_to_vote_value
from app.helpers import create_like_keyboard_markup
from app.helpers import get_global_rating
from app.helpers import get_monthly_rating
from app.helpers import month_number_to_name
from app.models import Photo
from app.models import TelegramUser
from app.models import Vote
from app.schemas import VoteActionEnum
from app.schemas import VoteCallbackData
from app.schemas import vote_callback

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot)


@dp.callback_query_handler(vote_callback.filter(action=[VoteActionEnum.UP, VoteActionEnum.DOWN]))
async def vote_callback_handler(
    callback_query: types.CallbackQuery,
    callback_data: dict[str, str],
):
    vote_callback_data = VoteCallbackData(**callback_data)
    user, _ = await TelegramUser.get_or_create_from_tg_user(callback_query.from_user)

    try:
        photo = await Photo.get(id=vote_callback_data.message_id).prefetch_related("author")
    except exceptions.DoesNotExist:
        await bot.answer_callback_query(callback_query.id, "Что-то пошло не так 💩")
        return

    if photo.author.id == user.id:
        await bot.answer_callback_query(callback_query.id, "Тебя никто не спрашивал!")
        return

    async with transactions.in_transaction():
        vote_value = action_to_vote_value(vote_callback_data.action)
        _, created = await Vote.create_user_vote(user=user, photo=photo, vote_value=vote_value)

        if not created:
            await bot.answer_callback_query(callback_query.id, "Первое слово дороже второго!")
            return

        markup = create_like_keyboard_markup(vote_callback_data.message_id, photo.likes, -photo.dislikes)
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=markup,
        )
        await bot.answer_callback_query(callback_query.id, "Твой голос учтён!")


@dp.callback_query_handler(vote_callback.filter(action=[VoteActionEnum.VOTES]))
async def vote_callback_votes_handler(
    callback_query: types.CallbackQuery,
    callback_data: dict[str, str],
):
    vote_callback_data = VoteCallbackData(**callback_data)

    votes = await Vote.filter(photo=vote_callback_data.message_id).prefetch_related("user")
    if not votes:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Картинку пока никто не оценил 🙈",
            reply_to_message_id=vote_callback_data.message_id,
            disable_notification=True,
            parse_mode="Markdown",
        )
        await callback_query.answer(cache_time=60)
        return

    text = "*Рейтинг картинки:*\n"
    text += "\n".join([f"{v.user.name}: {'👍' if v.value == 1 else '👎'}" for v in votes])

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=text,
        reply_to_message_id=vote_callback_data.message_id,
        disable_notification=True,
        parse_mode="Markdown",
    )
    await callback_query.answer(cache_time=60)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def photo_handler(message: types.Message):
    author, _ = await TelegramUser.get_or_create_from_tg_user(message.from_user)
    async with transactions.in_transaction():
        await Photo.get_or_create(id=message.message_id, author=author)
        reply_markup = create_like_keyboard_markup(message.message_id, 0, 0)
        await message.reply("Тебе понравилась эта картинка?", reply_markup=reply_markup)


@dp.message_handler(commands=["global_rating"])
async def global_rating_handler(message: types.Message):
    text = "*Глобальный рейтинг:*\n"
    rating = await get_global_rating()
    if not rating:
        await message.reply("Не найдено ни одного участника!")
        return
    text += "\n".join([f"{name}: {votes}" for name, votes in rating.items()])
    await bot.send_message(message.chat.id, text, parse_mode="Markdown")


@dp.message_handler(commands=["rating"])
async def monthly_rating_handler(message: types.Message):
    today: dt.date = dt.datetime.utcnow().date()
    month_name = month_number_to_name(today.month)
    text = f"*Рейтинг за {month_name}:*\n"
    rating = await get_monthly_rating(today.month)
    if not rating:
        await message.reply("Не найдено ни одного участника!")
        return
    text += "\n".join([f"{name}: {votes}" for name, votes in rating.items()])
    await bot.send_message(message.chat.id, text, parse_mode="Markdown")
