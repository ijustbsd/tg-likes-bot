import datetime as dt
import typing as t
from enum import StrEnum
from enum import auto

from aiogram import types
from tortoise import fields
from tortoise.models import Model

from app.config.bot import bot
from app.config.settings import settings


class TelegramUser(Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=256)
    first_name = fields.CharField(max_length=256)
    last_name = fields.CharField(max_length=256)
    rating = fields.IntField(default=0)

    @property
    def name(self) -> str:
        full_name = " ".join([self.first_name, self.last_name])
        if full_name != " ":
            return full_name
        elif self.username:
            return self.username
        return str(self.id)

    @classmethod
    async def get_or_create_from_tg_user(
        cls,
        tg_user: types.User,
    ) -> tuple["TelegramUser", bool]:
        return await cls.get_or_create(
            id=tg_user.id,
            defaults={
                "username": tg_user.username or "",
                "first_name": tg_user.first_name or "",
                "last_name": tg_user.last_name or "",
            },
        )


class Photo(Model):
    id = fields.BigIntField(pk=True)
    author: fields.ForeignKeyRelation["TelegramUser"] = fields.ForeignKeyField(
        "models.TelegramUser", related_name="photos"
    )
    likes = fields.IntField(default=0)
    dislikes = fields.IntField(default=0)
    created_at = fields.DatetimeField(default=dt.datetime.utcnow)


class Vote(Model):
    user: fields.ForeignKeyRelation["TelegramUser"] = fields.ForeignKeyField(
        "models.TelegramUser", related_name="votes"
    )
    photo: fields.ForeignKeyRelation["Photo"] = fields.ForeignKeyField("models.Photo", related_name="votes")
    value = fields.IntField()

    class Meta:
        unique_together = (("user", "photo"),)

    @classmethod
    async def create_user_vote(
        cls,
        user: TelegramUser,
        photo: Photo,
        vote_value: int,
    ) -> tuple[bool, t.Optional["Vote"]]:
        vote, created = await cls.get_or_create(
            user=user,
            photo=photo,
            defaults={"value": vote_value},
        )
        if not created:
            return False, None

        if vote_value > 0:
            photo.likes += vote_value
            await photo.save(update_fields=["likes"])
        elif vote_value < 0:
            photo.dislikes += vote_value
            await photo.save(update_fields=["dislikes"])

        photo.author.rating += vote_value
        await photo.author.save()

        return True, vote


class NotificationType(StrEnum):
    INFO = auto()
    MONTHLY_RATING = auto()
    DAILY_REMINDER = auto()


class Notification(Model):
    id = fields.IntField(pk=True)
    type = fields.CharEnumField(NotificationType, max_length=32)
    text = fields.TextField()
    parameters = fields.JSONField(default={})
    sent_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now=True)

    async def send(self):
        await bot.send_message(settings.TG_CHAT_ID, self.text, parse_mode="Markdown")
        self.sent_at = dt.datetime.utcnow()
        await self.save()
