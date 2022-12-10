import os
from datetime import datetime
from typing import Dict

import pytest
from asyncclick.testing import CliRunner
from pytest_httpx import HTTPXMock

from les_stats.client_api.riot import RiotAPI
from les_stats.models.internal.auth import Api, Scope
from les_stats.utils.auth import API_KEY_SIZE_MAX, get_digest
from les_stats.utils.config import get_settings
from les_stats.utils.import_match import import_matches_tft
from tests.utils import CustomClient, get_json_response

MOCKED_DATA_FOLDER = "riot/tft/"


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def tortoise_init_db(runner: CliRunner, client: CustomClient) -> None:
    for key in [
        ("write", "w" * API_KEY_SIZE_MAX, Scope.write),
        ("read", "r" * API_KEY_SIZE_MAX, Scope.read),
    ]:
        await Api.create(name=key[0], api_key=get_digest(key[1]), scope=key[2])


@pytest.mark.parametrize(
    (
        "puuid",
        "start_time",
        "api_key",
        "event",
        "tournament",
        "stage",
        "puuids_http_json",
        "min_player",
        "count_game",
        "end_time",
        "mock_puuid",
        "rc",
        "message",
    ),
    (
        (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Error: Missing argument 'PUUID'.",
        ),
        (
            {"value": ""},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Error: Missing argument 'PUUID'.",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Qa"
            },
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Usage: import-matches-tft [OPTIONS] PUUID\nTry 'import-matches-tft --help' for help.\n\nError: Missing option '--start-time'.\n",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Qa",
            },
            {"value": "", "option": "start-time"},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Usage: import-matches-tft [OPTIONS] PUUID\nTry 'import-matches-tft --help' for help.\n\nError: Missing option '--start-time'.\n",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Qa"
            },
            {"value": "2022-11-15 09:17:00", "option": "start-time"},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Usage: import-matches-tft [OPTIONS] PUUID\nTry 'import-matches-tft --help' for help.\n\nError: Missing option '--api-key'.\n",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Qa"
            },
            {"value": "2022-11-15 09:17:00", "option": "start-time"},
            {"value": "", "option": "api-key"},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Usage: import-matches-tft [OPTIONS] PUUID\nTry 'import-matches-tft --help' for help.\n\nError: Missing option '--api-key'.\n",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0QNotExist"
            },
            {"value": "2022-11-15 09:17:00", "option": "start-time"},
            {"value": "w" * API_KEY_SIZE_MAX, "option": "api-key"},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": True, "http_code": 400},
            1,
            "Error: 400: Bad Request - Exception decrypting ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0QNoExist",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Q"
            },
            {"value": "2022-11-15 09:17:00", "option": "start-time"},
            {"value": "KeyDoesNotExist", "option": "api-key"},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Invalid value: Invalid API Key\n",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Q"
            },
            {"value": "2022-11-15 09:17:00", "option": "start-time"},
            {"value": "r" * API_KEY_SIZE_MAX, "option": "api-key"},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": False},
            2,
            "Usage: import-matches-tft [OPTIONS] PUUID\nTry 'import-matches-tft --help' for help.\n\nError: Invalid value: Invalid API Key\n",
        ),
        (
            {
                "value": "ds8RFUB2gv7up-qeVc8xTS5jRitXQlVaE0y8038tirRJmtPlIw83dF_hds_UV4yGkxfxBDl551vi0Qa"
            },
            {"value": "2022-11-15 09:17:00", "option": "start-time"},
            {"value": "w" * API_KEY_SIZE_MAX, "option": "api-key"},
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {"test": True, "http_code": 200},
            0,
            "Game EUW1_5781372307 saved\nGame EUW1_5979031153 saved\n",
        ),
    ),
)
@pytest.mark.asyncio
async def test_import_matches_tft(
    runner: CliRunner,
    client: CustomClient,
    httpx_mock: HTTPXMock,
    tortoise_init_db: None,
    puuid: str,
    start_time: str,
    api_key: str,
    event: str,
    tournament: str,
    stage: str,
    puuids_http_json: Dict,
    min_player: str,
    count_game: str,
    end_time: str,
    mock_puuid: Dict,
    rc: int,
    message,
):
    cli_params = []
    for p in [
        puuid,
        api_key,
        start_time,
        end_time,
        count_game,
        min_player,
        puuids_http_json,
        stage,
        tournament,
        event,
    ]:
        if p is not None and len(p["value"]) > 0:
            if "option" in p:
                cli_params.append(f"--{p['option']}")
            cli_params.append(p["value"])

    if mock_puuid["test"]:
        params = "?start=0"

        if count_game:
            params += f"&count={count_game['value']}"
        else:
            params += "&count=20"
        if end_time:
            params += f"&endTime={datetime.strptime(end_time['value'], '%Y-%m-%d %H:%M:%S').timestamp()}"
        if start_time:
            params += f"&startTime={int(datetime.strptime(start_time['value'], '%Y-%m-%d %H:%M:%S').timestamp())}"

        matches = get_json_response(
            os.path.join(MOCKED_DATA_FOLDER, "match", puuid["value"] + ".json")
        )
        httpx_mock.add_response(
            method="GET",
            url=f"https://{get_settings().TFT_API_ROUTING}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid['value']}/ids{params}",
            status_code=mock_puuid["http_code"],
            json=matches,
        )

        if mock_puuid["http_code"] == 200:
            for match_id in matches:
                httpx_mock.add_response(
                    method="GET",
                    url=f"https://{RiotAPI.get_region(match_id)}.api.riotgames.com/tft/match/v1/matches/{match_id}",
                    status_code=200,
                    json=get_json_response(
                        os.path.join(MOCKED_DATA_FOLDER, "match", match_id + ".json")
                    ),
                )

    result = await runner.invoke(import_matches_tft, cli_params)
    assert result.exit_code == rc
    if rc != 0:
        assert result.exception
    assert message in str(result.output)
