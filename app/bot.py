import logging

from aiogram import Bot, Dispatcher, types
from tortoise import exceptions, transactions

from .config import settings
from .helpers import create_like_keyboard_markup, get_rating
from .models import Photo, TelegramUser, Vote
from .schemas import VoteActionEnum, VoteCallbackData, vote_callback

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)

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
        vote_value = 1 if vote_callback_data.action == VoteActionEnum.UP else -1

        _, created = await Vote.get_or_create(
            user=user,
            photo=photo,
            defaults={"value": vote_value},
        )
        if not created:
            await bot.answer_callback_query(callback_query.id, "Первое слово дороже второго!")
            return

        if vote_value > 0:
            photo.likes += vote_value
            await photo.save(update_fields=["likes"])
        elif vote_value < 0:
            photo.dislikes += vote_value
            await photo.save(update_fields=["dislikes"])

        photo.author.rating += vote_value
        await photo.author.save()

        markup = create_like_keyboard_markup(vote_callback_data.message_id, photo.likes, -photo.dislikes)
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=markup,
        )
        await bot.answer_callback_query(callback_query.id, "Твой голос учтён!")


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def photo_handler(message: types.Message):
    author, _ = await TelegramUser.get_or_create_from_tg_user(message.from_user)
    async with transactions.in_transaction():
        await Photo.create(id=message.message_id, author=author)
        reply_markup = create_like_keyboard_markup(message.message_id, 0, 0)
        await message.reply("Тебе понравилась эта картинка?", reply_markup=reply_markup)


@dp.message_handler(commands=["rating"])
async def rating_handler(message: types.Message):
    text = "*Рейтинг участников:*\n"
    rating = await get_rating()
    if not rating:
        await message.reply("Не найдено ни одного участника!")
        return
    text += "\n".join([f"{name}: {votes}" for name, votes in rating.items()])
    await bot.send_message(message.chat.id, text, parse_mode="Markdown")
