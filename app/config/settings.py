import logging
import typing as t

from pydantic import Field
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

    HOST: str = "127.0.0.1"
    PORT: int = Field(6969, alias="PORT")
    URL: str = "localhost"
    WEBHOOK_SECRET: str = "secret"
    WEBHOOK_PATH: str = "/webhook"

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


settings = Settings()

# для aerich
TORTOISE_ORM = settings.TORTOISE_ORM
