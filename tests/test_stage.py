from typing import Generator

import pytest
from fastapi.testclient import TestClient

from les_stats.schemas.internal.stage import Stage_Pydantic
from tests.utils import create_stage_by_db

NAMESPACE = "/internal/stage/"


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
            200,
        ),
    ),
)
@pytest.mark.anyio
def test_post_stage(
    client: TestClient,
    event_loop: Generator,
    j_data: Stage_Pydantic,
    http_code: int,
):
    response = client.post(
        f"{NAMESPACE}",
        json=j_data,
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
            "Bracket",
            200,
        ),
    ),
)
@pytest.mark.anyio
def test_get_stages(
    client: TestClient, event_loop: Generator, id: int, name: str, http_code: int
):
    event_loop.run_until_complete(create_stage_by_db(name))

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
        ("Bracket", 200, "", True),
        ("Bracket158", 404, "Stage Bracket158 not found", False),
    ),
)
@pytest.mark.anyio
def test_get_stage(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_stage_by_db(name))

    response = client.get(f"{NAMESPACE}{name}")
    print(response.json())
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
@pytest.mark.anyio
def test_delete_stage(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_stage_by_db(name))

    response = client.delete(f"{NAMESPACE}{name}")
    print(response.json())
    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["message"] == message
    elif http_code == 404:
        assert data["detail"] == message
