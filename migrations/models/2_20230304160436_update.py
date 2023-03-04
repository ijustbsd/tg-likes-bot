from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "notification" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(32) NOT NULL,
    "text" TEXT NOT NULL,
    "parameters" JSONB NOT NULL,
    "sent_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "notification"."type" IS 'INFO: info\nMONTHLY_RATING: monthly_rating';;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "notification";"""
