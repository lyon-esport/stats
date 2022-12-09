from tortoise import Tortoise, connections

from les_stats.utils.config import get_settings


async def init_db() -> None:
    await Tortoise.init(
        db_url=get_settings().DB_URL,
        modules={"models": ["les_stats.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await connections.close_all()
