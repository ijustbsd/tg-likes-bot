import datetime as dt
import logging

from aiogram import Dispatcher
from aiogram import F
from aiogram import Router
from aiogram import types
from aiogram.filters.command import Command
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
from app.schemas import VoteCallback

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

router = Router(name=__name__)


@router.callback_query(VoteCallback.filter(F.action.in_({VoteActionEnum.UP, VoteActionEnum.DOWN})))
async def vote_callback_handler(
    callback_query: types.CallbackQuery,
    callback_data: VoteCallback,
):
    if callback_query.message is None:
        await bot.answer_callback_query(callback_query.id, "Что-то пошло не так 💩")
        return

    user, _ = await TelegramUser.get_or_create_from_tg_user(callback_query.from_user)

    try:
        photo = await Photo.get(id=callback_data.message_id).prefetch_related("author")
    except exceptions.DoesNotExist:
        await bot.answer_callback_query(callback_query.id, "Что-то пошло не так 💩")
        return

    if photo.author.id == user.id:
        await bot.answer_callback_query(callback_query.id, "Тебя никто не спрашивал!")
        return

    async with transactions.in_transaction():
        vote_value = action_to_vote_value(callback_data.action)
        _, created = await Vote.create_user_vote(user=user, photo=photo, vote_value=vote_value)

        if not created:
            await bot.answer_callback_query(callback_query.id, "Первое слово дороже второго!")
            return

        markup = create_like_keyboard_markup(callback_data.message_id, photo.likes, -photo.dislikes)
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=markup,
        )
        await bot.answer_callback_query(callback_query.id, "Твой голос учтён!")


@router.callback_query(VoteCallback.filter(F.action == VoteActionEnum.VOTES))
async def vote_callback_votes_handler(
    callback_query: types.CallbackQuery,
    callback_data: VoteCallback,
):
    if callback_query.message is None:
        await bot.answer_callback_query(callback_query.id, "Что-то пошло не так 💩")
        return

    votes = await Vote.filter(photo=callback_data.message_id).prefetch_related("user")
    if not votes:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Картинку пока никто не оценил 🙈",
            reply_to_message_id=callback_data.message_id,
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
        reply_to_message_id=callback_data.message_id,
        disable_notification=True,
        parse_mode="Markdown",
    )
    await callback_query.answer(cache_time=60)


@router.message(F.content_type == types.ContentType.PHOTO)
async def photo_handler(message: types.Message):
    if message.from_user is None:
        await message.reply("Не удалось определить автора картинки 🙈")
        return

    author, _ = await TelegramUser.get_or_create_from_tg_user(message.from_user)
    async with transactions.in_transaction():
        await Photo.get_or_create(id=message.message_id, author=author)
        reply_markup = create_like_keyboard_markup(message.message_id, 0, 0)
        await message.reply("Тебе понравилась эта картинка?", reply_markup=reply_markup)


@router.message(Command("global_rating"))
async def global_rating_handler(message: types.Message):
    text = "*Глобальный рейтинг:*\n"
    rating = await get_global_rating()
    if not rating:
        await message.reply("Не найдено ни одного участника!")
        return
    text += "\n".join([f"{name}: {votes}" for name, votes in rating.items()])
    await bot.send_message(message.chat.id, text, parse_mode="Markdown")


@router.message(Command("rating"))
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


dp.include_router(router)
