from aiogram import types

from .models import TelegramUser
from .schemas import VoteActionEnum, vote_callback


def create_like_keyboard_markup(
    message_id: int,
    like_count: int,
    dislike_count: int,
) -> types.InlineKeyboardMarkup:
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    data_like = vote_callback.new(message_id=message_id, action=VoteActionEnum.UP)
    data_dislike = vote_callback.new(message_id=message_id, action=VoteActionEnum.DOWN)
    keyboard_markup.add(
        types.InlineKeyboardButton(f"👍 {like_count}", callback_data=data_like),
        types.InlineKeyboardButton(f"👎 {dislike_count}", callback_data=data_dislike),
    )
    return keyboard_markup


def action_to_vote_value(action: VoteActionEnum) -> int:
    return {
        VoteActionEnum.UP: 1,
        VoteActionEnum.DOWN: -1,
    }[action]


async def get_rating() -> dict[str, int]:
    rating = {}
    users = await TelegramUser.all().order_by("-rating")
    for user in users:
        rating[user.name] = user.rating
    return rating
