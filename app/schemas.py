from enum import StrEnum

from aiogram.utils.callback_data import CallbackData
from pydantic import BaseModel


class VoteActionEnum(StrEnum):
    UP = "up"
    DOWN = "down"
    VOTES = "votes"


class VoteCallbackData(BaseModel):
    message_id: int
    action: VoteActionEnum


vote_callback = CallbackData("vote_v1", *VoteCallbackData.__fields__.keys())
