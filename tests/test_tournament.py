from typing import Generator

import pytest
from fastapi.testclient import TestClient

from tests.utils import create_tournament_by_db, update_tournament_by_db

NAMESPACE = "/internal/tournament/"


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "http_code",
        "message",
    ),
    ((1, "Pro", 200, ""),),
)
@pytest.mark.anyio
def test_post_tournament(
    client: TestClient,
    event_loop: Generator,
    id: int,
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
    assert data["id"] == id
    assert data["name"] == name


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "http_code",
    ),
    (
        (
            1,
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
    assert data[id - 1]["id"] == id
    assert data[id - 1]["name"] == name


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "http_code",
        "message",
    ),
    (
        (1, "Pro", 200, ""),
        (0, "Pro", 404, "Tournament 0 not found"),
    ),
)
@pytest.mark.anyio
def test_get_tournament(
    client: TestClient,
    event_loop: Generator,
    id: int,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_tournament_by_db(name))

    response = client.get(f"{NAMESPACE}{id}")

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["id"] == id
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "http_code",
        "message",
    ),
    (
        (1, "Pro", 200, "Deleted Tournament 1"),
        (0, "Pro", 404, "Tournament 0 not found"),
    ),
)
@pytest.mark.anyio
def test_delete_tournament(
    client: TestClient,
    event_loop: Generator,
    id: int,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_tournament_by_db(name))

    response = client.delete(f"{NAMESPACE}{id}")

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["message"] == message
    elif http_code == 404:
        assert data["detail"] == message


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "http_code",
        "message",
    ),
    (
        (1, "Elite", 200, ""),
        (0, "Elite", 404, "Tournament 0 not found"),
    ),
)
@pytest.mark.anyio
def test_put_tournaments(
    client: TestClient,
    event_loop: Generator,
    id: int,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_tournament_by_db(name))
    event_loop.run_until_complete(update_tournament_by_db(id, name))

    response = client.put(f"{NAMESPACE}{id}", json={"name": name})

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["id"] == id
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message
