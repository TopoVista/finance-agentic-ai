from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from pymongo.errors import PyMongoError

from api.core.config import settings
from api.models.report import Report
from api.models.report_setting import ReportSetting
from api.models.transaction import Transaction
from api.models.user import User

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    database = client[settings.DB_NAME]
    try:
        await client.admin.command("ping")
        await init_beanie(
            database=database,
            document_models=[User, Transaction, Report, ReportSetting],
        )
    except PyMongoError as exc:
        print(f"[finora] MongoDB unavailable at startup: {exc}")
        database = None


async def disconnect_db() -> None:
    global client, database
    if client is not None:
        client.close()
    client = None
    database = None


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("Database has not been initialized.")
    return database
