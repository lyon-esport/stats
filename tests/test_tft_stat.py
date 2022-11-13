import os

import pytest
from pytest_httpx import HTTPXMock

from les_stats.client_api.riot import RiotAPI, RiotHost
from les_stats.models.internal.auth import Scope
from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from tests.utils import CustomClient, get_json_response

NAMESPACE = "/tft/stat/"
MOCKED_DATA_FOLDER = "riot/tft/match/"
API_RESPONSE_DATA = "les_stats/tft/stats/"
ENDPOINTS = [
    "tier-list/composition",
    "tier-list/item",
    "tier-list/unit",
    "player/{player_id}/placement",
    "player/{player_id}/kill",
    "player/{player_id}/death-round",
    "games/damage",
    "games/time",
    "game/{match_id}/damage",
]


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def tortoise_init_db(client: CustomClient, httpx_mock: HTTPXMock) -> None:
    data = [
        (
            "EUW1_5781372307",
            "event",
            "tournament",
            "stage",
        ),
        (
            "EUW1_5979031153",
            "",
            "",
            "",
        ),
    ]
    for match_id, event, tournament, stage in data:
        j_data = {"id": match_id}
        if event:
            await Event.get_or_create(name=event)
            j_data["event"] = event
        if tournament:
            await Tournament.get_or_create(name=tournament)
            j_data["tournament"] = tournament
        if stage:
            await Stage.get_or_create(name=stage)
            j_data["stage"] = stage

        httpx_mock.add_response(
            method="GET",
            url=f"https://{RiotAPI.get_region(match_id)}.api.riotgames.com/tft/match/v1/matches/{match_id}",
            status_code=200,
            json=get_json_response(
                os.path.join(MOCKED_DATA_FOLDER, match_id + ".json")
            ),
        )
        await client.test_api(
            "POST",
            "/tft/game/matches/save",
            Scope.write,
            json=[j_data],
        )


@pytest.mark.parametrize(
    ("endpoint",),
    (
        ("tier-list/composition",),
        ("tier-list/item",),
        ("tier-list/unit",),
        ("player/test/placement",),
        ("player/test/kill",),
        ("player/test/death-round",),
        ("games/damage",),
        ("games/time",),
        ("game/test/damage",),
    ),
)
@pytest.mark.asyncio
async def test_scopes(client: CustomClient, endpoint: str):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}{endpoint}", [Scope.read, Scope.write]
    )


@pytest.mark.parametrize(
    (
        "event",
        "tournament",
        "stage",
        "match_id",
        "player_id",
        "region",
        "http_code",
        "api_filename_response",
    ),
    (
        (
            None,
            None,
            None,
            "EUW1_5781372307",
            "AJ1iPPJY2wyNq3Ke4-COeaWq55Oq-QFM2DEQEDJ-LZ0_vnltbmLTT5UEA8pv5kd7Mh_M5GLJpcj8Rw",
            RiotHost.europe,
            200,
            "all.json",
        ),
        (
            "event",
            None,
            None,
            "EUW1_5781372307",
            "AJ1iPPJY2wyNq3Ke4-COeaWq55Oq-QFM2DEQEDJ-LZ0_vnltbmLTT5UEA8pv5kd7Mh_M5GLJpcj8Rw",
            RiotHost.europe,
            200,
            "one.json",
        ),
        (
            None,
            "tournament",
            None,
            "EUW1_5781372307",
            "AJ1iPPJY2wyNq3Ke4-COeaWq55Oq-QFM2DEQEDJ-LZ0_vnltbmLTT5UEA8pv5kd7Mh_M5GLJpcj8Rw",
            RiotHost.europe,
            200,
            "one.json",
        ),
        (
            None,
            None,
            "stage",
            "EUW1_5781372307",
            "AJ1iPPJY2wyNq3Ke4-COeaWq55Oq-QFM2DEQEDJ-LZ0_vnltbmLTT5UEA8pv5kd7Mh_M5GLJpcj8Rw",
            RiotHost.europe,
            200,
            "one.json",
        ),
        (
            "test",
            "test",
            "test",
            "test",
            "test",
            RiotHost.europe,
            404,
            "not_found.json",
        ),
    ),
)
@pytest.mark.asyncio
async def test_endpoints(
    client: CustomClient,
    tortoise_init_db: None,
    event: str,
    tournament: str,
    stage: str,
    match_id: str,
    player_id: str,
    region: RiotHost,
    http_code: int,
    api_filename_response: str,
):
    params = ""
    if event:
        params = f"?event={event}"
    if tournament:
        params += f"{'?' if len(params) == 0 else '&'}tournament={tournament}"
    if stage:
        params += f"{'?' if len(params) == 0 else '&'}stage={stage}"
    if region:
        params += f"{'?' if len(params) == 0 else '&'}region={region}"

    for endpoint in ENDPOINTS:
        url = f"{NAMESPACE}{endpoint.format(match_id=match_id, player_id=player_id)}"

        response = await client.test_api("GET", f"{url}{params}", Scope.read)
        expected_response = get_json_response(
            os.path.join(API_RESPONSE_DATA, endpoint, api_filename_response)
        )
        assert response.status_code == http_code
        assert response.json() == expected_response
