from typing import List

import asyncclick as click
from tortoise import Tortoise

from les_stats.models.valorant.game import ValorantArmor, ValorantWeapon
from les_stats.routers.valorant.utils import insert_match_data
from les_stats.utils.config import get_settings


async def init_db(db_url: str) -> None:
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["les_stats.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()


@click.group()
async def db() -> None:
    await init_db(get_settings().DB_URL)


@db.result_callback()
async def process_result(result, **kwargs):
    await close_db()


@click.command()
async def load_valorant_data() -> None:
    from pyot.conf.utils import import_confs

    from ..models.valorant.game import ValorantCharacter

    import_confs("les_stats.utils.pyot_config")
    from pyot.models import val

    content = await val.Content().get()
    print(f"{len(content.characters)} characters to load")
    for character in content.characters:
        char_id = character.id.lower()
        name = character.name
        await ValorantCharacter.update_or_create(id=char_id, defaults={"name": name})
    for equip in content.equips:
        char_id = equip.id.lower()
        name = equip.name
        await ValorantWeapon.update_or_create(id=char_id, defaults={"name": name})
        await ValorantArmor.update_or_create(id=char_id, defaults={"name": name})

    for character in content.characters:
        char_id = character.id.lower()
        name = character.name
        await ValorantCharacter.update_or_create(id=char_id, defaults={"name": name})


@click.command()
@click.argument("game_name")
@click.argument("tag")
async def add_player(game_name: str, tag: str) -> None:
    from pyot.conf.utils import import_confs

    from ..models.valorant.game import ValorantPlayer

    import_confs("les_stats.utils.pyot_config")
    # noqa: F401
    from pyot.models import riot, val  # noqa: F401

    content = await riot.Account(game_name=game_name, tag_line=tag).using("val").get()
    if not content:
        return

    await ValorantPlayer.update_or_create(
        puuid=content.puuid,
        defaults={"game_name": content.game_name, "tag_line": content.tag_line},
    )


@click.command()
@click.argument("game_name")
@click.argument("tag")
async def load_match(game_name: str, tag: str) -> None:
    from pyot.conf.utils import import_confs
    from pyot.core.queue import Queue

    from ..models.valorant.game import ValorantPlayer

    import_confs("les_stats.utils.pyot_config")
    from pyot.models import riot, val

    content = await riot.Account(game_name=game_name, tag_line=tag).using("val").get()
    if not content:
        return

    player, _ = await ValorantPlayer.get_or_create(
        puuid=content.puuid,
        defaults={"game_name": content.game_name, "tag_line": content.tag_line},
    )

    history = await val.MatchHistory(puuid=content.puuid).get()
    async with Queue() as queue:
        for match in history.history[:40]:
            await queue.put(match.get())
        first_10_matches: List[val.Match] = await queue.join()

    for match in first_10_matches:
        await insert_match_data(match)


db.add_command(load_valorant_data)
db.add_command(add_player)
db.add_command(load_match)

if __name__ == "__main__":
    db(_anyio_backend="asyncio")
