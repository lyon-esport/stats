from tortoise import Tortoise


async def init_db(db_url: str) -> None:
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["les_stats.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()
