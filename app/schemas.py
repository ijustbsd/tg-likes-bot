from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class VoteActionEnum(StrEnum):
    UP = "up"
    DOWN = "down"
    VOTES = "votes"


class VoteCallback(CallbackData, prefix="vote_v1"):
    message_id: int
    action: VoteActionEnum
