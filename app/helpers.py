from collections import defaultdict

from aiogram import types

from .models import Photo
from .models import TelegramUser
from .schemas import VoteActionEnum
from .schemas import vote_callback


def create_like_keyboard_markup(
    message_id: int,
    like_count: int,
    dislike_count: int,
) -> types.InlineKeyboardMarkup:
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    data_like = vote_callback.new(message_id=message_id, action=VoteActionEnum.UP)
    data_dislike = vote_callback.new(message_id=message_id, action=VoteActionEnum.DOWN)
    data_votes = vote_callback.new(message_id=message_id, action=VoteActionEnum.VOTES)
    keyboard_markup.add(
        types.InlineKeyboardButton(f"👍 {like_count}", callback_data=data_like),
        types.InlineKeyboardButton(f"👎 {dislike_count}", callback_data=data_dislike),
        types.InlineKeyboardButton("👀", callback_data=data_votes),
    )
    return keyboard_markup


def action_to_vote_value(action: VoteActionEnum) -> int:
    return {
        VoteActionEnum.UP: 1,
        VoteActionEnum.DOWN: -1,
    }[action]


async def get_global_rating() -> dict[str, int]:
    rating = {}
    users = await TelegramUser.filter(rating__not=0).order_by("-rating")
    for user in users:
        rating[user.name] = user.rating
    return rating


async def get_monthly_rating(month: int) -> dict[str, int]:
    photos: list[Photo] = await Photo.filter(created_at__month=month).prefetch_related("author")
    rating: defaultdict[str, int] = defaultdict(int)
    for photo in photos:
        rating[photo.author.name] += photo.likes - photo.dislikes
    return dict(sorted(rating.items(), key=lambda x: x[1], reverse=True))


def month_number_to_name(month: int) -> str:
    return [
        "январь",
        "февраль",
        "март",
        "апрель",
        "май",
        "июнь",
        "июль",
        "август",
        "сентябрь",
        "октябрь",
        "ноябрь",
        "декабрь",
    ][month - 1]
