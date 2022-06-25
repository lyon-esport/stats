from typing import Generator

import pytest
from fastapi.testclient import TestClient

from les_stats.schemas.internal.tournament import (
    Tournament_Pydantic,
    TournamentIn_Pydantic,
)
from tests.utils import create_tournament_by_db

NAMESPACE = "/internal/tournament/"


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
            200,
            False,
        ),
        (
            {"name": "Pro2", "stages": [{"test": "Bracket"}]},
            422,
            False,
        ),
        (
            {"name": "Pro2", "stages": [{"name": "Bracket"}, {"name": "Bracket2"}]},
            200,
            False,
        ),
    ),
)
@pytest.mark.anyio
def test_post_tournament(
    client: TestClient,
    event_loop: Generator,
    j_data: Tournament_Pydantic,
    http_code: int,
    dupplicate: bool,
):
    exec_time = 1
    if dupplicate:
        exec_time = 2

    for _ in range(0, exec_time):
        response = client.post(f"{NAMESPACE}", json=j_data)

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
@pytest.mark.anyio
def test_get_tournaments(
    client: TestClient, event_loop: Generator, id: int, name: str, http_code: int
):
    event_loop.run_until_complete(create_tournament_by_db(name))

    response = client.get(f"{NAMESPACE}")

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
@pytest.mark.anyio
def test_get_tournament(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_tournament_by_db(name))

    response = client.get(f"{NAMESPACE}{name}")

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
@pytest.mark.anyio
def test_delete_tournament(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_tournament_by_db(name))

    response = client.delete(f"{NAMESPACE}{name}")

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
@pytest.mark.anyio
def test_put_tournaments(
    client: TestClient,
    event_loop: Generator,
    name: str,
    j_data: TournamentIn_Pydantic,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_tournament_by_db(name))

    response = client.put(f"{NAMESPACE}{name}", json=j_data)

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message
