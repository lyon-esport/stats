from typing import Dict, Union

import pytest

from les_stats.models.internal.auth import Scope
from les_stats.models.internal.stage import Stage
from les_stats.schemas.internal.stage import Stage_Pydantic
from tests.utils import CustomClient

NAMESPACE = "/internal/stage"


@pytest.mark.parametrize(
    ("method", "endpoint", "json", "scopes"),
    (
        ("POST", "", {"name": "test"}, [Scope.write]),
        ("GET", "", {}, [Scope.write, Scope.read]),
        ("GET", "/test", {}, [Scope.write, Scope.read]),
        ("DELETE", "/test", {}, [Scope.write]),
    ),
)
@pytest.mark.asyncio
async def test_scopes(
    client: CustomClient,
    method: str,
    endpoint: str,
    json: Dict[str, str],
    scopes: Union[Scope.write, Scope.read],
):
    await client.test_api_scope(method, f"{NAMESPACE}{endpoint}", scopes, json=json)


@pytest.mark.parametrize(
    (
        "j_data",
        "http_code",
    ),
    (
        (
            {
                "ffff": "Bracket",
            },
            422,
        ),
        (
            {
                "name": "Bracket",
            },
            201,
        ),
    ),
)
@pytest.mark.asyncio
async def test_post_stage(
    client: CustomClient,
    j_data: Stage_Pydantic,
    http_code: int,
):
    response = await client.test_api("POST", f"{NAMESPACE}", Scope.write, json=j_data)

    assert response.status_code == http_code

    data = response.json()
    if http_code == 200:
        assert data["name"] == j_data["name"]


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "http_code",
    ),
    (
        (
            0,
            "Bracket",
            200,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_stages(client: CustomClient, id: int, name: str, http_code: int):
    await Stage.create(name=name)

    response = await client.test_api("GET", f"{NAMESPACE}", Scope.read)

    assert response.status_code == http_code
    data = response.json()
    assert data[id]["name"] == name


@pytest.mark.parametrize(
    (
        "name",
        "http_code",
        "message",
        "create",
    ),
    (
        ("Bracket", 200, "", True),
        ("Bracket158", 404, "Stage Bracket158 not found", False),
    ),
)
@pytest.mark.asyncio
async def test_get_stage(
    client: CustomClient,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Stage.create(name=name)

    response = await client.test_api("GET", f"{NAMESPACE}/{name}", Scope.read)

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message


@pytest.mark.parametrize(
    (
        "name",
        "http_code",
        "message",
        "create",
    ),
    (
        ("Bracket", 200, "Deleted Stage Bracket", True),
        ("Bracket158", 404, "Stage Bracket158 not found", False),
    ),
)
@pytest.mark.asyncio
async def test_delete_stage(
    client: CustomClient,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Stage.create(name=name)

    response = await client.test_api("DELETE", f"{NAMESPACE}/{name}", Scope.write)

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["message"] == message
    elif http_code == 404:
        assert data["detail"] == message
