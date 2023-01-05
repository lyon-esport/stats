from typing import Union
from urllib.parse import urlparse

import asyncclick as click
import httpx

from les_stats.client_api.riot import GameSaveIn_Pydantic, RiotAPI, RiotGame
from les_stats.models.internal.auth import Scope
from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from les_stats.utils.auth import is_api_key_scope_valid
from les_stats.utils.config import get_settings
from les_stats.utils.db import close_db, init_db


def validate_url(
    ctx: click.Context, param: click.Parameter, value: Union[str, None]
) -> str:
    if value is not None:
        try:
            urlparse(value)
        except Exception:
            raise click.UsageError("Incorrect url given")

    return value


@click.group()
async def cli() -> None:
    await init_db()


@cli.result_callback()
async def process_result(result, **kwargs):
    await close_db()


@click.command()
@click.option(
    "--event",
    default=None,
    help="Event name",
)
@click.option(
    "--tournament",
    default=None,
    help="Tournament name",
)
@click.option(
    "--stage",
    default=None,
    help="Stage name",
)
@click.option(
    "--puuids-http-json",
    default=None,
    callback=validate_url,
    help="PUUID players json file used to match player",
)
@click.option(
    "--min-player",
    type=click.IntRange(min=1, max=8),
    default=1,
    help="Minimum number of players that must be in game",
)
@click.option(
    "--count-game",
    type=click.IntRange(min=1, max=100),
    default=20,
    help="Number of game to fetch on selected player",
)
@click.option(
    "--end-time",
    type=click.DateTime(formats=["%Y-%m-%d %H:%M:%S"]),
    default=None,
    help="Game must start before end-time",
)
@click.option(
    "--start-time",
    type=click.DateTime(formats=["%Y-%m-%d %H:%M:%S"]),
    required=True,
    help="Game must start after start-time",
)
@click.option(
    "--api-key",
    required=True,
    help="API Key used to import matches",
)
@click.argument("puuid")
async def import_matches_tft(
    puuid: str,
    api_key: str,
    start_time: click.DateTime,
    end_time: click.DateTime,
    count_game: click.IntRange,
    min_player: click.IntRange,
    puuids_http_json: str,
    event: str,
    tournament: str,
    stage: str,
) -> None:
    if not await is_api_key_scope_valid(api_key, [Scope.write]):
        raise click.BadParameter("Invalid API Key")

    if event and await Event.filter(name=event).count() != 1:
        raise click.ClickException(f"Event {event} does not exist")
    if tournament and await Tournament.filter(name=tournament).count() != 1:
        raise click.ClickException(f"Tournament {tournament} does not exist")
    if stage and await Stage.filter(name=stage).count() != 1:
        raise click.ClickException(f"Stage {stage} does not exist")

    players = []

    if puuids_http_json:
        r = httpx.get(puuids_http_json, headers={"accept": "application/json"})
        if not httpx.codes.is_success(r.status_code):
            raise click.ClickException(f"puuids-http-json {r.status_code}: {r.text}")

        players = [player["puuid"] for player in r.json()["players"]]

    status_code, datas = await RiotAPI(RiotGame.tft).get_matches_list(
        [puuid],
        0,
        end_time.strftime("%s") if end_time else None,
        start_time.strftime("%s"),
        count_game,
    )
    data = datas[0]

    if not httpx.codes.is_success(status_code):
        raise click.ClickException(
            f"{data.error.status_code}: {data.error.message['status']['message']}"
        )

    if len(data.data) == 0:
        click.secho("No match found", fg="green")
    else:
        payloads = []
        for match_id in data.data:
            payloads.append(
                GameSaveIn_Pydantic(
                    event=event,
                    tournament=tournament,
                    stage=stage,
                    id=match_id,
                )
            )

        status_code, matches = await RiotAPI(RiotGame.tft).save_tft_games(
            payloads, min_player=min_player, players=players
        )

        if not httpx.codes.is_success(status_code) and status_code != 409:
            raise click.ClickException(
                f"{status_code}: {matches.json()['error']}", fg="yellow"
            )

        for data in matches:
            if data.error is None:
                click.secho(data.data, fg="green")
            else:
                click.secho(
                    f"{data.error.status_code}: {data.error.message}", fg="yellow"
                )


if (
    get_settings().TFT_API_KEY is not None
    and get_settings().TFT_API_ROUTING is not None
):
    cli.add_command(import_matches_tft)

if __name__ == "__main__":
    cli(_anyio_backend="asyncio")
