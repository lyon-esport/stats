from typing import Generator

import pytest
from fastapi.testclient import TestClient

from tests.utils import create_stage_by_db

NAMESPACE = "/internal/stage/"


@pytest.mark.parametrize(
    (
        "name",
        "http_code",
        "message",
    ),
    (("Bracket", 200, ""),),
)
@pytest.mark.anyio
def test_post_stage(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
):
    response = client.post(
        f"{NAMESPACE}",
        json={
            "name": name,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == name


@pytest.mark.parametrize(
    (
        "name",
        "http_code",
    ),
    (
        (
            "Bracket",
            200,
        ),
    ),
)
@pytest.mark.anyio
def test_get_stages(
    client: TestClient, event_loop: Generator, name: str, http_code: int
):
    event_loop.run_until_complete(create_stage_by_db(name))

    response = client.get(f"{NAMESPACE}")

    assert response.status_code == http_code
    data = response.json()
    assert data[id - 1]["name"] == name


@pytest.mark.parametrize(
    (
        "name",
        "http_code",
        "message",
    ),
    (
        ("Bracket", 200, ""),
        ("Bracket", 404, "Stage 0 not found"),
    ),
)
@pytest.mark.anyio
def test_get_stage(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_stage_by_db(name))

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
    ),
    (
        ("Bracket", 200, "Deleted Stage 1"),
        ("Bracket", 404, "Stage 0 not found"),
    ),
)
@pytest.mark.anyio
def test_delete_stage(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_stage_by_db(name))

    response = client.delete(f"{NAMESPACE}{id}")

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["message"] == message
    elif http_code == 404:
        assert data["detail"] == message
