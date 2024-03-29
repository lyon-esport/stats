import os
from typing import Dict, List, Union

import httpx
import pytest
from pytest_httpx import HTTPXMock

from les_stats.client_api.riot import RiotAPI
from les_stats.models.internal.auth import Scope
from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from les_stats.models.tft.game import TFTGame
from les_stats.utils.config import get_settings
from tests.utils import CustomClient, get_json_response

NAMESPACE = "/tft/game/"
MOCKED_DATA_FOLDER = "riot/tft/match/"


@pytest.mark.parametrize(
    ("method", "endpoint", "json", "scopes"),
    (
        ("GET", "match-list", {}, [Scope.write, Scope.read]),
        ("GET", "matches", {}, [Scope.write, Scope.read]),
        ("GET", "matches/save", {}, [Scope.write, Scope.read]),
        ("PUT", "matches/save", [{"id": "test"}], [Scope.write]),
        ("DELETE", "matches/save", ["test"], [Scope.write]),
    ),
)
@pytest.mark.asyncio
async def test_generic_scopes(
    client: CustomClient,
    method: str,
    endpoint: str,
    json: Dict[str, str],
    scopes: Union[Scope.write, Scope.read],
):
    await client.test_api_scope(method, f"{NAMESPACE}{endpoint}", scopes, json=json)


@pytest.mark.parametrize(
    (
        "infos",
        "start",
        "end_time",
        "start_time",
        "count",
        "http_code",
    ),
    (
        (
            [
                {
                    "puuid": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Q",
                    "http_code": 200,
                },
            ],
            0,
            0,
            0,
            20,
            200,
        ),
        (
            [
                {
                    "puuid": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0QNotExist",
                    "http_code": 400,
                },
            ],
            0,
            0,
            0,
            20,
            400,
        ),
        (
            [
                {
                    "puuid": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Q",
                    "http_code": 200,
                },
                {
                    "puuid": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0QNotExist",
                    "http_code": 400,
                },
            ],
            0,
            0,
            0,
            20,
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_matches_from_summoners(
    client: CustomClient,
    httpx_mock: HTTPXMock,
    infos: List[Dict[str, Union[str, int]]],
    start: int,
    end_time: int,
    start_time: int,
    count: int,
    http_code: int,
):
    url = f"{NAMESPACE}match-list?start={start}&count={count}"
    if end_time:
        url = f"{url}&end_time={end_time}"
    if start_time:
        url = f"{url}&start_time={start_time}"

    for i in range(0, len(infos)):
        url = f"{url}&puuid={infos[i]['puuid']}"
        mocked_url = f"https://{get_settings().TFT_API_ROUTING}.api.riotgames.com/tft/match/v1/matches/by-puuid/{infos[i]['puuid']}/ids?start={start}&count={count}"
        if end_time:
            mocked_url = f"{mocked_url}?endTime={end_time}"
        if start_time:
            mocked_url = f"{mocked_url}?startTime={start_time}"
        httpx_mock.add_response(
            method="GET",
            url=mocked_url,
            status_code=infos[i]["http_code"],
            json=get_json_response(
                os.path.join(MOCKED_DATA_FOLDER, infos[i]["puuid"] + ".json")
            ),
        )

    response = await client.test_api("GET", url, Scope.read)

    assert response.status_code == http_code
    datas = response.json()

    for i in range(0, len(infos)):
        if httpx.codes.is_success(infos[i]["http_code"]):
            assert datas[i]["error"] is None
            assert datas[i]["data"] is not None
        else:
            assert datas[i]["data"] is None
            assert datas[i]["error"]["status_code"] == infos[i]["http_code"]
            assert datas[i]["error"]["message"] is not None


@pytest.mark.parametrize(
    (
        "infos",
        "http_code",
    ),
    (
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "http_code": 200,
                },
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5979031153",
                    "http_code": 200,
                },
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "http_code": 400,
                },
            ],
            400,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "http_code": 200,
                },
                {
                    "match_id": "EUW1_5979031153",
                    "http_code": 200,
                },
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "http_code": 400,
                },
            ],
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_matches_stat_from_a_list_of_game(
    client: CustomClient,
    httpx_mock: HTTPXMock,
    infos: List[Dict[str, Union[str, int]]],
    http_code: int,
):
    url = f"{NAMESPACE}matches"

    for i in range(0, len(infos)):
        if i == 0:
            url = f"{url}?match_id={infos[i]['match_id']}"
        else:
            url = f"{url}&match_id={infos[i]['match_id']}"
        httpx_mock.add_response(
            method="GET",
            url=f"https://{RiotAPI.get_region(infos[i]['match_id'])}.api.riotgames.com/tft/match/v1/matches/{infos[i]['match_id']}",
            status_code=infos[i]["http_code"],
            json=get_json_response(
                os.path.join(MOCKED_DATA_FOLDER, infos[i]["match_id"] + ".json")
            ),
        )

    response = await client.test_api("GET", url, Scope.read)

    assert response.status_code == http_code
    datas = response.json()

    for i in range(0, len(infos)):
        if httpx.codes.is_success(infos[i]["http_code"]):
            assert datas[i]["error"] is None
            assert datas[i]["data"] is not None
        else:
            assert datas[i]["data"] is None
            assert datas[i]["error"]["status_code"] == infos[i]["http_code"]
            assert datas[i]["error"]["message"] is not None


@pytest.mark.parametrize(
    (
        "matches_to_create",
        "filters",
        "result",
        "http_code",
    ),
    (
        (
            [
                {
                    "match_id": "EUW1_5979031153",
                    "event": None,
                    "tournament": None,
                    "stage": None,
                },
            ],
            {
                "event": None,
                "tournament": None,
                "stage": None,
            },
            [{"match_id": "EUW1_5979031153"}],
            200,
        ),
        (
            [],
            {
                "event": None,
                "tournament": None,
                "stage": None,
            },
            None,
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5979031153",
                    "event": "test",
                    "tournament": None,
                    "stage": None,
                },
            ],
            {
                "event": "test",
                "tournament": None,
                "stage": None,
            },
            [{"match_id": "EUW1_5979031153"}],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "event": None,
                    "tournament": "tests",
                    "stage": "aaaa",
                },
                {
                    "match_id": "EUW1_5979031153",
                    "event": None,
                    "tournament": "test",
                    "stage": None,
                },
            ],
            {
                "event": None,
                "tournament": "test",
                "stage": None,
            },
            [{"match_id": "EUW1_5979031153"}],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "event": None,
                    "tournament": None,
                    "stage": "aaaa",
                },
                {
                    "match_id": "EUW1_5979031153",
                    "event": None,
                    "tournament": None,
                    "stage": "test",
                },
            ],
            {
                "event": None,
                "tournament": None,
                "stage": "test",
            },
            [{"match_id": "EUW1_5979031153"}],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "event": "fff",
                    "tournament": None,
                    "stage": "test",
                },
                {
                    "match_id": "EUW1_5979031153",
                    "event": None,
                    "tournament": "fff",
                    "stage": "test",
                },
            ],
            {
                "event": None,
                "tournament": None,
                "stage": "test",
            },
            [{"match_id": "EUW1_5781372307"}, {"match_id": "EUW1_5979031153"}],
            200,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_matches_in_stat_system(
    client: CustomClient,
    httpx_mock: HTTPXMock,
    matches_to_create: List[Dict[str, Union[str, None]]],
    filters: Dict[str, str],
    result: List[Dict[str, str]],
    http_code: int,
):
    j_datas = []
    for match in matches_to_create:
        j_data = {"id": match["match_id"]}
        if match["event"]:
            await Event.get_or_create(name=match["event"])
            j_data["event"] = match["event"]
        if match["tournament"]:
            await Tournament.get_or_create(name=match["tournament"])
            j_data["tournament"] = match["tournament"]
        if match["stage"]:
            await Stage.get_or_create(name=match["stage"])
            j_data["stage"] = match["stage"]

        httpx_mock.add_response(
            method="GET",
            url=f"https://{RiotAPI.get_region(match['match_id'])}.api.riotgames.com/tft/match/v1/matches/{match['match_id']}",
            status_code=200,
            json=get_json_response(
                os.path.join(MOCKED_DATA_FOLDER, match["match_id"] + ".json")
            ),
        )
        j_datas.append(j_data)

    await client.test_api(
        "POST",
        f"{NAMESPACE}matches/save",
        Scope.write,
        json=j_datas,
    )

    params = ""
    if filters["event"]:
        params = f"?event={filters['event']}"
    if filters["tournament"]:
        params += (
            f"{'?' if len(params) == 0 else '&'}tournament={filters['tournament']}"
        )
    if filters["stage"]:
        params += f"{'?' if len(params) == 0 else '&'}stage={filters['stage']}"

    response = await client.test_api(
        "GET",
        f"{NAMESPACE}matches/save{params}",
        Scope.read,
    )

    assert response.status_code == http_code
    data = response.json()

    if httpx.codes.is_success(http_code):
        assert data["error"] is None or (
            data["data"] is None
            and httpx.codes.is_success(data["error"]["status_code"])
        )
        assert data["data"] == result
    else:
        assert "data" not in data
        assert data["detail"] is not None


@pytest.mark.asyncio
async def test_save_matches_scopes(client: CustomClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"https://{RiotAPI.get_region('EUW1_5979031153')}.api.riotgames.com/tft/match/v1/matches/EUW1_5979031153",
        status_code=200,
        json=get_json_response(
            os.path.join(MOCKED_DATA_FOLDER, "EUW1_5979031153.json")
        ),
    )
    await client.test_api_scope(
        "POST",
        f"{NAMESPACE}matches/save",
        [Scope.write],
        json=[{"id": "EUW1_5979031153"}],
    )


@pytest.mark.parametrize(
    ("infos", "http_code"),
    (
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "mock": True,
                    "http_code": 200,
                    "event": None,
                    "tournament": None,
                    "stage": None,
                },
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "mock": True,
                    "http_code": 200,
                    "event": {"name": "Lyon e-Sport", "create": True},
                    "tournament": None,
                    "stage": None,
                }
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "mock": True,
                    "http_code": 200,
                    "event": None,
                    "tournament": {"name": "Pro", "create": True},
                    "stage": None,
                }
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "mock": True,
                    "http_code": 200,
                    "event": None,
                    "tournament": None,
                    "stage": {"name": "Bracket", "create": True},
                }
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "mock": False,
                    "http_code": 404,
                    "event": {"name": "Lyon e-Sport", "create": False},
                    "tournament": None,
                    "stage": None,
                }
            ],
            404,
        ),
        (
            [
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "mock": True,
                    "http_code": 404,
                    "event": None,
                    "tournament": None,
                    "stage": None,
                },
            ],
            404,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "mock": True,
                    "http_code": 200,
                    "event": {"name": "Lyon e-Sport", "create": True},
                    "tournament": None,
                    "stage": None,
                },
                {
                    "match_id": "EUW1_5979031153",
                    "mock": True,
                    "http_code": 200,
                    "event": {"name": "Lyon e-Sport", "create": False},
                    "tournament": None,
                    "stage": {"name": "Bracket", "create": True},
                },
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "mock": True,
                    "http_code": 404,
                    "event": None,
                    "tournament": None,
                    "stage": None,
                },
            ],
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_save_matches(
    client: CustomClient,
    httpx_mock: HTTPXMock,
    infos: List[Dict[str, Union[str, int]]],
    http_code: int,
):
    j_data = []

    for i in range(0, len(infos)):
        data = {}
        if infos[i]["event"]:
            if infos[i]["event"]["create"]:
                await Event.create(name=infos[i]["event"]["name"])
            data["event"] = infos[i]["event"]["name"]
        if infos[i]["tournament"]:
            if infos[i]["tournament"]["create"]:
                await Tournament.create(name=infos[i]["tournament"]["name"])
            data["tournament"] = infos[i]["tournament"]["name"]
        if infos[i]["stage"]:
            if infos[i]["stage"]["create"]:
                await Stage.create(name=infos[i]["stage"]["name"])
            data["stage"] = infos[i]["stage"]["name"]

        data["id"] = infos[i]["match_id"]
        j_data.append(data)
        if infos[i]["mock"]:
            httpx_mock.add_response(
                method="GET",
                url=f"https://{RiotAPI.get_region(infos[i]['match_id'])}.api.riotgames.com/tft/match/v1/matches/{infos[i]['match_id']}",
                status_code=infos[i]["http_code"],
                json=get_json_response(
                    os.path.join(MOCKED_DATA_FOLDER, infos[i]["match_id"] + ".json")
                ),
            )

    response = await client.test_api(
        "POST", f"{NAMESPACE}matches/save", Scope.write, json=j_data
    )

    assert response.status_code == http_code
    datas = response.json()

    for i in range(0, len(infos)):
        if httpx.codes.is_success(infos[i]["http_code"]):
            assert datas[i]["error"] is None
            assert datas[i]["data"] is not None
        else:
            assert datas[i]["data"] is None
            assert datas[i]["error"]["status_code"] == infos[i]["http_code"]
            assert datas[i]["error"]["message"] is not None


@pytest.mark.parametrize(
    ("infos", "http_code"),
    (
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 200,
                    "event": None,
                    "tournament": None,
                    "stage": None,
                },
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 200,
                    "event": {"name": "Lyon e-Sport", "create": True},
                    "tournament": None,
                    "stage": None,
                }
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 200,
                    "event": None,
                    "tournament": {"name": "Pro", "create": True},
                    "stage": None,
                }
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 200,
                    "event": None,
                    "tournament": None,
                    "stage": {"name": "Bracket", "create": True},
                }
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 404,
                    "event": {"name": "Lyon e-Sport", "create": False},
                    "tournament": None,
                    "stage": None,
                }
            ],
            404,
        ),
        (
            [
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "create": False,
                    "http_code": 404,
                    "event": None,
                    "tournament": None,
                    "stage": None,
                },
            ],
            404,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 200,
                    "event": {"name": "Lyon e-Sport", "create": True},
                    "tournament": None,
                    "stage": None,
                },
                {
                    "match_id": "EUW1_5979031153",
                    "create": True,
                    "http_code": 200,
                    "event": {"name": "Lyon e-Sport", "create": False},
                    "tournament": None,
                    "stage": {"name": "Bracket", "create": True},
                },
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "create": False,
                    "http_code": 404,
                    "event": None,
                    "tournament": None,
                    "stage": None,
                },
            ],
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_update_matches(
    client: CustomClient,
    infos: List[Dict[str, Union[str, int]]],
    http_code: int,
):
    j_data = []

    for i in range(0, len(infos)):
        data = {}
        if infos[i]["event"]:
            if infos[i]["event"]["create"]:
                await Event.create(name=infos[i]["event"]["name"])
            data["event"] = infos[i]["event"]["name"]
        if infos[i]["tournament"]:
            if infos[i]["tournament"]["create"]:
                await Tournament.create(name=infos[i]["tournament"]["name"])
            data["tournament"] = infos[i]["tournament"]["name"]
        if infos[i]["stage"]:
            if infos[i]["stage"]["create"]:
                await Stage.create(name=infos[i]["stage"]["name"])
            data["stage"] = infos[i]["stage"]["name"]

        if infos[i]["create"]:
            await TFTGame.create(
                match_id=infos[i]["match_id"],
                data_version="",
                game_datetime=0,
                game_length=0.0,
                game_version="",
                queue_id=0,
                tft_set_number=0,
                tft_game_type="",
            )
        data["id"] = infos[i]["match_id"]
        j_data.append(data)

    response = await client.test_api(
        "PUT", f"{NAMESPACE}matches/save", Scope.write, json=j_data
    )

    assert response.status_code == http_code
    datas = response.json()

    for i in range(0, len(infos)):
        if httpx.codes.is_success(infos[i]["http_code"]):
            assert datas[i]["error"] is None
            assert datas[i]["data"] is not None
        else:
            assert datas[i]["data"] is None
            assert datas[i]["error"]["status_code"] == infos[i]["http_code"]
            assert datas[i]["error"]["message"] is not None


@pytest.mark.parametrize(
    (
        "infos",
        "http_code",
    ),
    (
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 200,
                },
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5979031153",
                    "create": True,
                    "http_code": 200,
                },
            ],
            200,
        ),
        (
            [
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "create": False,
                    "http_code": 404,
                },
            ],
            404,
        ),
        (
            [
                {
                    "match_id": "EUW1_5781372307",
                    "create": True,
                    "http_code": 200,
                },
                {
                    "match_id": "EUW1_5979031153",
                    "create": True,
                    "http_code": 200,
                },
                {
                    "match_id": "EUW1_5979031153NotExist",
                    "create": False,
                    "http_code": 404,
                },
            ],
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_delete_matches(
    client: CustomClient, infos: List[Dict[str, Union[str, int]]], http_code: int
):
    j_data = []

    for i in range(0, len(infos)):
        j_data.append(infos[i]["match_id"])
        if infos[i]["create"]:
            await TFTGame.create(
                match_id=infos[i]["match_id"],
                data_version="",
                game_datetime=0,
                game_length=0.0,
                game_version="",
                queue_id=0,
                tft_set_number=0,
                tft_game_type="",
            )

    response = await client.test_api(
        "DELETE", f"{NAMESPACE}matches/save", Scope.write, json=j_data
    )

    assert response.status_code == http_code
    datas = response.json()

    for i in range(0, len(infos)):
        if httpx.codes.is_success(infos[i]["http_code"]):
            assert datas[i]["error"] is None
            assert datas[i]["data"] is not None
        else:
            assert datas[i]["data"] is None
            assert datas[i]["error"]["status_code"] == infos[i]["http_code"]
            assert datas[i]["error"]["message"] is not None
