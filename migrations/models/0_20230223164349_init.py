from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "telegramuser" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(256) NOT NULL,
    "first_name" VARCHAR(256) NOT NULL,
    "last_name" VARCHAR(256) NOT NULL,
    "rating" INT NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "photo" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "likes" INT NOT NULL  DEFAULT 0,
    "dislikes" INT NOT NULL  DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "author_id" BIGINT NOT NULL REFERENCES "telegramuser" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "vote" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "value" INT NOT NULL,
    "photo_id" BIGINT NOT NULL REFERENCES "photo" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "telegramuser" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_vote_user_id_1c41cf" UNIQUE ("user_id", "photo_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
