from typing import Generator

import pytest
from fastapi.testclient import TestClient

from tests.utils import create_tournament_by_db, update_tournament_by_db

NAMESPACE = "/internal/tournament/"


@pytest.mark.parametrize(
    (
        "name",
        "http_code",
        "message",
    ),
    (("Pro", 200, ""),),
)
@pytest.mark.anyio
def test_post_tournament(
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
            "Pro",
            200,
        ),
    ),
)
@pytest.mark.anyio
def test_get_tournaments(
    client: TestClient, event_loop: Generator, name: str, http_code: int
):
    event_loop.run_until_complete(create_tournament_by_db(name))

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
        ("Pro", 200, ""),
        ("Pro", 404, "Tournament 0 not found"),
    ),
)
@pytest.mark.anyio
def test_get_tournament(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
):
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
    ),
    (
        ("Pro", 200, "Deleted Tournament 1"),
        ("Pro", 404, "Tournament 0 not found"),
    ),
)
@pytest.mark.anyio
def test_delete_tournament(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
):
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
        "http_code",
        "message",
    ),
    (
        ("Elite", 200, ""),
        ("Elite", 404, "Tournament 0 not found"),
    ),
)
@pytest.mark.anyio
def test_put_tournaments(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_tournament_by_db(name))
    event_loop.run_until_complete(update_tournament_by_db(name))

    response = client.put(f"{NAMESPACE}{name}", json={"name": name})

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message
