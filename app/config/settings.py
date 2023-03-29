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

    REDIS_PROTOCOL: str = "redis"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str = "bot"
    REDIS_PASSWORD: str = "bot"
    REDIS_VHOST: str = ""

    REDIS: dict[str, t.Any] = {}

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
        values["REDIS"].update(
            {
                "protocol": values["REDIS_PROTOCOL"],
                "host": values["REDIS_HOST"],
                "port": values["REDIS_PORT"],
                "user": values["REDIS_USER"],
                "password": values["REDIS_PASSWORD"],
                "db_number": values["REDIS_VHOST"],
            }
        )
        return values


settings = Settings()

# для aerich
TORTOISE_ORM = settings.TORTOISE_ORM

CELERY_BROKER_URL = "{protocol}://{user}:{password}@{host}:{port}/{db_number}".format_map(settings.REDIS)
