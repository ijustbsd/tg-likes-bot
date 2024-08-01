import logging
import typing as t

from pydantic import model_validator
from pydantic_settings import BaseSettings

logging.root.setLevel(logging.INFO)


class Settings(BaseSettings):
    BOT_TOKEN: str = "1337:BOT_TOKEN"

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "bot"
    DB_PASSWORD: str = "bot"
    DB_NAME: str = "bot"

    TORTOISE_ORM: dict[str, t.Any] = {}

    RABBITMQ_PROTOCOL: str = "amqp"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "bot"
    RABBITMQ_PASSWORD: str = "bot"
    RABBITMQ_VHOST: str = ""

    RABBITMQ: dict[str, t.Any] = {}

    TG_CHAT_ID: int = 0

    class Config:
        env_file = ".env"
        env_prefix = "APP_"

    @model_validator(mode="after")
    def set_tortoise_orm(self) -> t.Self:
        self.TORTOISE_ORM = {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_NAME,
                    },
                },
            },
            "apps": {
                "models": {
                    "models": ["app.models", "aerich.models"],
                },
            },
        }
        return self

    @model_validator(mode="after")
    def set_rabbitmq(self) -> t.Self:
        self.RABBITMQ = {
            "protocol": self.RABBITMQ_PROTOCOL,
            "host": self.RABBITMQ_HOST,
            "port": self.RABBITMQ_PORT,
            "user": self.RABBITMQ_USER,
            "password": self.RABBITMQ_PASSWORD,
            "vhost": self.RABBITMQ_VHOST,
        }
        return self


settings = Settings()

# для aerich
TORTOISE_ORM = settings.TORTOISE_ORM

CELERY_BROKER_URL = "{protocol}://{user}:{password}@{host}:{port}/{vhost}".format_map(settings.RABBITMQ)
