from aiogram import types
from tortoise import fields
from tortoise.models import Model


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
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "last_name": tg_user.last_name,
            },
        )


class Photo(Model):
    id = fields.BigIntField(pk=True)
    author: fields.ForeignKeyRelation["TelegramUser"] = fields.ForeignKeyField(
        "models.TelegramUser", related_name="photos"
    )
    likes = fields.IntField(default=0)
    dislikes = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now=True)

    @property
    def rating(self) -> int:
        return self.likes + self.dislikes


class Vote(Model):
    user: fields.ForeignKeyRelation["TelegramUser"] = fields.ForeignKeyField(
        "models.TelegramUser", related_name="votes"
    )
    photo: fields.ForeignKeyRelation["Photo"] = fields.ForeignKeyField("models.Photo", related_name="votes")
    value = fields.IntField()

    class Meta:
        unique_together = (("user", "photo"),)
