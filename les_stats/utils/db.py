from typing import List

import asyncclick as click
from tortoise import Tortoise

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
@click.argument("type")
async def load_valorant_data(type: str) -> None:
    from pyot.conf.utils import import_confs

    from ..models.valorant.game import ValorantCharacter

    import_confs("les_stats.utils.pyot_config")
    from pyot.models import val

    content = await val.Content().get()
    print(f"{len(content.characters)} characters to load")
    for character in content.characters:
        char_id = character.id.lower()
        name = character.name
        await ValorantCharacter.update_or_create(
            character_id=char_id, defaults={"name": name}
        )


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

    from ..models.valorant.game import ValorantGame, ValorantPlayer, ValorantTeam

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
        for match in history.history[:10]:
            await queue.put(match.get())
        first_10_matches: List[val.Match] = await queue.join()

    for match in first_10_matches:
        match_db, _ = await ValorantGame.update_or_create(
            match_id=match.id,
            defaults={
                "start_time": match.start_time,
                "length": match.info.length.total_seconds(),
                "map_url": match.info.map_url,
                "is_completed": match.info.is_completed,
                "game_mode": match.info.game_mode,
            },
        )

        for participant in match.players:
            account = await participant.account.get()

            player, _ = await ValorantPlayer.get_or_create(
                puuid=account.puuid,
                defaults={"game_name": account.game_name, "tag_line": account.tag_line},
            )
            print(participant.team_id)
            if participant.team_id not in ("Red", "Blue"):
                continue
            await ValorantTeam.get_or_create(
                game=match_db, player=player, defaults={"team": participant.team_id}
            )


db.add_command(load_valorant_data)
db.add_command(add_player)
db.add_command(load_match)

if __name__ == "__main__":
    db(_anyio_backend="asyncio")
