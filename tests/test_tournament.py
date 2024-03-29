from typing import Dict, Union

import pytest

from les_stats.models.internal.auth import Scope
from les_stats.models.internal.tournament import Tournament
from les_stats.schemas.internal.tournament import (
    Tournament_Pydantic,
    TournamentIn_Pydantic,
)
from tests.utils import CustomClient

NAMESPACE = "/internal/tournament"


@pytest.mark.parametrize(
    ("method", "endpoint", "json", "scopes"),
    (
        ("POST", "", {"name": "test"}, [Scope.write]),
        ("GET", "", {}, [Scope.write, Scope.read]),
        ("GET", "/test", {}, [Scope.write, Scope.read]),
        ("DELETE", "/test", {}, [Scope.write]),
        ("PUT", "/test", {}, [Scope.write]),
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
    ("j_data", "http_code", "dupplicate"),
    (
        (
            {
                "ffff": "Pro",
            },
            422,
            False,
        ),
        (
            {
                "name": "Pro",
            },
            409,
            True,
        ),
        (
            {
                "name": "Pro",
            },
            201,
            False,
        ),
        (
            {"name": "Pro2", "stages": [{"test": "Bracket"}]},
            422,
            False,
        ),
        (
            {"name": "Pro2", "stages": [{"name": "Bracket"}, {"name": "Bracket2"}]},
            201,
            False,
        ),
    ),
)
@pytest.mark.asyncio
async def test_post_tournament(
    client: CustomClient,
    j_data: Tournament_Pydantic,
    http_code: int,
    dupplicate: bool,
):
    exec_time = 1
    if dupplicate:
        exec_time = 2

    for _ in range(0, exec_time):
        response = await client.test_api(
            "POST", f"{NAMESPACE}", Scope.write, json=j_data
        )

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
            "Pro",
            200,
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_tournaments(
    client: CustomClient, id: int, name: str, http_code: int
):
    await Tournament.create(name=name)

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
        ("Pro", 200, "", True),
        ("Pro158", 404, "Tournament Pro158 not found", False),
    ),
)
@pytest.mark.asyncio
async def test_get_tournament(
    client: CustomClient,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Tournament.create(name=name)

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
        ("Pro", 200, "Deleted Tournament Pro", True),
        ("Pro158", 404, "Tournament Pro158 not found", False),
    ),
)
@pytest.mark.asyncio
async def test_delete_tournament(
    client: CustomClient,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Tournament.create(name=name)

    response = await client.test_api("DELETE", f"{NAMESPACE}/{name}", Scope.write)

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["message"] == message
    elif http_code == 404:
        assert data["detail"] == message


@pytest.mark.parametrize(
    (
        "name",
        "j_data",
        "http_code",
        "message",
        "create",
    ),
    (
        ("Pro158", {}, 404, "Tournament Pro158 not found", False),
        ("Pro", {}, 200, "", True),
        (
            "Pro2",
            {"stages": [{"test": "Bracket"}]},
            422,
            "",
            True,
        ),
        (
            "Pro2",
            {"stages": [{"name": "Bracket"}, {"name": "Bracket2"}]},
            200,
            "",
            True,
        ),
    ),
)
@pytest.mark.asyncio
async def test_put_tournaments(
    client: CustomClient,
    name: str,
    j_data: TournamentIn_Pydantic,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Tournament.create(name=name)

    response = await client.test_api(
        "PUT", f"{NAMESPACE}/{name}", Scope.write, json=j_data
    )

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message
