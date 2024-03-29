from typing import List

import pytest
from asyncclick.testing import CliRunner

from les_stats.utils.auth import (
    API_KEY_SIZE_MAX,
    API_KEY_SIZE_MIN,
    create_api_key,
    delete_api_key,
    list_api_key,
)
from tests.utils import CustomClient


@pytest.mark.parametrize(
    (
        "name",
        "scope",
        "rc",
        "message",
    ),
    (
        (None, "read", 2, "Error: Missing argument 'NAME'."),
        (
            "",
            "read",
            2,
            "Usage: create-api-key [OPTIONS] NAME\nTry 'create-api-key --help' for help.\n\nError: Invalid value: Name can't be empty\n",
        ),
        (
            "test",
            "",
            2,
            "Usage: create-api-key [OPTIONS] NAME\nTry 'create-api-key --help' for help.\n\nError: Invalid value: Invalid scope\n",
        ),
        ("test", None, 0, ""),
        ("test", "read", 0, ""),
        ("test", "write", 0, ""),
    ),
)
@pytest.mark.asyncio
async def test_create_api_key(
    runner: CliRunner, client: CustomClient, name: str, scope: str, rc: int, message
):
    if name is None:
        params = []
    elif scope is None:
        params = [name]
    else:
        params = [name, "--scope", scope]

    result = await runner.invoke(create_api_key, params)
    assert result.exit_code == rc
    if rc != 0:
        assert result.exception
        assert message in str(result.output)
    else:
        assert API_KEY_SIZE_MIN <= len(result.output) <= API_KEY_SIZE_MAX


@pytest.mark.parametrize(
    (
        "name",
        "rc",
        "message",
    ),
    (
        (None, 2, "Error: Missing argument 'NAME'."),
        (
            "",
            2,
            "Usage: delete-api-key [OPTIONS] NAME\nTry 'delete-api-key --help' for help.\n\nError: Invalid value: NAME can't be empty\n",
        ),
        (
            "test2",
            2,
            "Usage: delete-api-key [OPTIONS] NAME\nTry 'delete-api-key --help' for help.\n\nError: Invalid value: NAME not found\n",
        ),
        ("test", 0, ""),
    ),
)
@pytest.mark.asyncio
async def test_delete_api_key(
    runner: CliRunner, client: CustomClient, name: str, rc: int, message: str
):
    await runner.invoke(create_api_key, ["test"])
    if name is None:
        params = []
    else:
        params = [name]
    result = await runner.invoke(delete_api_key, params)

    assert result.exit_code == rc
    if rc != 0:
        assert result.exception
        assert message in str(result.output)
    else:
        assert result.output != ""


@pytest.mark.parametrize(
    ("api_keys",),
    (
        ([],),
        (["test", "test2"],),
    ),
)
@pytest.mark.asyncio
async def test_list_api_key(
    runner: CliRunner, client: CustomClient, api_keys: List[List[str]]
):
    output = ""
    for api_key in api_keys:
        await runner.invoke(create_api_key, [api_key])
        output = output + f"name: {api_key}, scope: read\n"

    result = await runner.invoke(list_api_key, [])

    assert result.exit_code == 0
    if len(api_keys) == 0:
        assert "No API Key exist" in result.output
    else:
        assert result.output == output
