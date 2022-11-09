import os
from typing import Dict, List, Union

import httpx
import pytest
from pytest_httpx import HTTPXMock

from les_stats.models.internal.auth import Scope
from tests.utils import CustomClient, get_json_response

NAMESPACE = "/tft/summoner/"
MOCKED_DATA_FOLDER = "riot/tft/summoner/"


@pytest.mark.parametrize(
    ("endpoint",),
    (
        ("by-puuid",),
        ("by-name",),
        ("rank",),
    ),
)
@pytest.mark.asyncio
async def test_scopes(client: CustomClient, endpoint: str):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}{endpoint}", [Scope.read, Scope.write]
    )


@pytest.mark.parametrize(
    (
        "infos",
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
            200,
        ),
        (
            [
                {
                    "puuid": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0QNotExist",
                    "http_code": 400,
                },
            ],
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
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_summoners_by_puuid(
    client: CustomClient,
    httpx_mock: HTTPXMock,
    infos: List[Dict[str, Union[str, int]]],
    http_code: int,
):
    url = f"{NAMESPACE}by-puuid"

    for i in range(0, len(infos)):
        if i == 0:
            url = f"{url}?encrypted_puuid={infos[i]['puuid']}"
        else:
            url = f"{url}&encrypted_puuid={infos[i]['puuid']}"

        httpx_mock.add_response(
            method="GET",
            url=f"https://euw1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{infos[i]['puuid']}",
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
                    "name": "MöNsTeRRR",
                    "http_code": 200,
                },
            ],
            200,
        ),
        (
            [
                {
                    "name": "MöNsTeRRRNotExist",
                    "http_code": 400,
                },
            ],
            400,
        ),
        (
            [
                {
                    "name": "MöNsTeRRR",
                    "http_code": 200,
                },
                {
                    "name": "MöNsTeRRRNotExist",
                    "http_code": 400,
                },
            ],
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_summoners_by_name(
    client: CustomClient,
    httpx_mock: HTTPXMock,
    infos: List[Dict[str, Union[str, int]]],
    http_code: int,
):
    url = f"{NAMESPACE}by-name"

    for i in range(0, len(infos)):
        if i == 0:
            url = f"{url}?summoner_name={infos[i]['name']}"
        else:
            url = f"{url}&summoner_name={infos[i]['name']}"

        httpx_mock.add_response(
            method="GET",
            url=f"https://euw1.api.riotgames.com/tft/summoner/v1/summoners/by-name/{infos[i]['name']}",
            status_code=infos[i]["http_code"],
            json=get_json_response(
                os.path.join(MOCKED_DATA_FOLDER, infos[i]["name"] + ".json")
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
                    "summoner_id": "0WjTGzOhQKB8AmejAbqsEEcZPAS8VGclP1-bpNWCVtgUHfz_oP-wksui4w",
                    "http_code": 200,
                },
            ],
            200,
        ),
        (
            [
                {
                    "summoner_id": "0WjTGzOhQKB8AmejAbqsEEcZPAS8VGclP1-bpNWCVtgUHfz_oP-wksui4wNotExist",
                    "http_code": 400,
                },
            ],
            400,
        ),
        (
            [
                {
                    "summoner_id": "0WjTGzOhQKB8AmejAbqsEEcZPAS8VGclP1-bpNWCVtgUHfz_oP-wksui4w",
                    "http_code": 200,
                },
                {
                    "summoner_id": "0WjTGzOhQKB8AmejAbqsEEcZPAS8VGclP1-bpNWCVtgUHfz_oP-wksui4wNotExist",
                    "http_code": 400,
                },
            ],
            207,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_summoners_rank(
    client: CustomClient,
    httpx_mock: HTTPXMock,
    infos: List[Dict[str, Union[str, int]]],
    http_code: int,
):
    url = f"{NAMESPACE}rank"

    for i in range(0, len(infos)):
        if i == 0:
            url = f"{url}?summoner_id={infos[i]['summoner_id']}"
        else:
            url = f"{url}&summoner_id={infos[i]['summoner_id']}"

        httpx_mock.add_response(
            method="GET",
            url=f"https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/{infos[i]['summoner_id']}",
            status_code=infos[i]["http_code"],
            json=get_json_response(
                os.path.join(MOCKED_DATA_FOLDER, infos[i]["summoner_id"] + ".json")
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
