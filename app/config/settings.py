import typing as t

from pydantic import BaseSettings, root_validator


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

    @root_validator
    @classmethod
    def post_init(cls, values: dict[str, t.Any]) -> dict[str, t.Any]:
        values["TORTOISE_ORM"].update(
            {
                "connections": {
                    "default": {
                        "engine": "tortoise.backends.asyncpg",
                        "credentials": {
                            "host": values["DB_HOST"],
                            "port": values["DB_PORT"],
                            "user": values["DB_USER"],
                            "password": values["DB_PASSWORD"],
                            "database": values["DB_NAME"],
                        },
                    },
                },
                "apps": {
                    "models": {
                        "models": ["app.models", "aerich.models"],
                    },
                },
            }
        )
        values["RABBITMQ"].update(
            {
                "protocol": values["RABBITMQ_PROTOCOL"],
                "host": values["RABBITMQ_HOST"],
                "port": values["RABBITMQ_PORT"],
                "user": values["RABBITMQ_USER"],
                "password": values["RABBITMQ_PASSWORD"],
                "vhost": values["RABBITMQ_VHOST"],
            }
        )
        return values


settings = Settings()

# для aerich
TORTOISE_ORM = settings.TORTOISE_ORM

CELERY_BROKER_URL = "{protocol}://{user}:{password}@{host}:{port}/{vhost}".format_map(settings.RABBITMQ)
