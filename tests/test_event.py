from typing import Generator

import pytest
from fastapi.testclient import TestClient

from tests.utils import create_event_by_db, update_event_by_db

NAMESPACE = "/event/"


@pytest.mark.parametrize(
    (
        "id",
        "name",
        "http_code",
        "message",
    ),
    ((1, "Lyon e-Sport 2022", 200, ""),),
)
@pytest.mark.anyio
def test_post_event(
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
            "Lyon e-Sport 2022",
            200,
        ),
    ),
)
@pytest.mark.anyio
def test_get_events(
    client: TestClient, event_loop: Generator, id: int, name: str, http_code: int
):
    event_loop.run_until_complete(create_event_by_db(name))

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
        (1, "Lyon e-Sport 2022", 200, ""),
        (0, "Lyon e-Sport 2022", 404, "Event 0 not found"),
    ),
)
@pytest.mark.anyio
def test_get_event(
    client: TestClient,
    event_loop: Generator,
    id: int,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_event_by_db(name))

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
        (1, "Lyon e-Sport 2022", 200, "Deleted Event 1"),
        (0, "Lyon e-Sport 2022", 404, "Event 0 not found"),
    ),
)
@pytest.mark.anyio
def test_delete_event(
    client: TestClient,
    event_loop: Generator,
    id: int,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_event_by_db(name))

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
        (1, "LAN Party", 200, ""),
        (0, "LAN Party", 404, "Event 0 not found"),
    ),
)
@pytest.mark.anyio
def test_put_events(
    client: TestClient,
    event_loop: Generator,
    id: int,
    name: str,
    http_code: int,
    message: str,
):
    event_loop.run_until_complete(create_event_by_db(name))
    event_loop.run_until_complete(update_event_by_db(id, name))

    response = client.put(f"{NAMESPACE}{id}", json={"name": name})

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["id"] == id
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message
