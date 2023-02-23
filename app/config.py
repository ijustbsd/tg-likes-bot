import typing as t

from pydantic import BaseSettings, root_validator


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "bot"
    DB_PASSWORD: str = "bot"
    DB_NAME: str = "bot"

    TORTOISE_ORM: dict[str, t.Any] = {}

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
        return values


settings = Settings()

# для aerich
TORTOISE_ORM = settings.TORTOISE_ORM
