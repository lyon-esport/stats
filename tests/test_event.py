from typing import Generator

import pytest
from fastapi.testclient import TestClient

from les_stats.schemas.internal.event import Event_Pydantic, EventIn_Pydantic
from tests.utils import create_event_by_db

NAMESPACE = "/internal/event/"


@pytest.mark.parametrize(
    ("j_data", "http_code", "dupplicate"),
    (
        (
            {
                "ffff": "Lyon e-Sport1",
            },
            422,
            False,
        ),
        (
            {
                "name": "Lyon e-Sport1",
            },
            409,
            True,
        ),
        (
            {
                "name": "Lyon e-Sport1",
            },
            200,
            False,
        ),
        (
            {"name": "Lyon e-Sport2", "tournaments": [{"test": "Pro"}]},
            422,
            False,
        ),
        (
            {
                "name": "Lyon e-Sport2",
                "tournaments": [{"name": "Pro"}, {"name": "Pro2"}],
            },
            200,
            False,
        ),
        (
            {
                "name": "Lyon e-Sport3",
                "tournaments": [{"name": "Pro", "stages": [{"test": "Bracket"}]}],
            },
            422,
            False,
        ),
        (
            {
                "name": "Lyon e-Sport3",
                "tournaments": [
                    {"name": "Pro", "stages": [{"name": "Bracket"}]},
                    {"name": "Pro2", "stages": [{"name": "Bracket"}]},
                ],
            },
            200,
            False,
        ),
    ),
)
@pytest.mark.anyio
def test_post_event(
    client: TestClient,
    event_loop: Generator,
    j_data: Event_Pydantic,
    http_code: int,
    dupplicate: bool,
):
    exec_time = 1
    if dupplicate:
        exec_time = 2

    for _ in range(0, exec_time):
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
        "name",
        "http_code",
    ),
    (
        (
            "Lyon e-Sport",
            200,
        ),
    ),
)
@pytest.mark.anyio
def test_get_events(
    client: TestClient, event_loop: Generator, name: str, http_code: int
):
    event_loop.run_until_complete(create_event_by_db(name))

    response = client.get(f"{NAMESPACE}")

    assert response.status_code == http_code
    data = response.json()
    assert data[0]["name"] == name


@pytest.mark.parametrize(
    (
        "name",
        "http_code",
        "message",
        "create",
    ),
    (
        ("Lyon e-Sport", 200, "", True),
        ("Lyon e-Sport", 404, "Event Lyon e-Sport not found", False),
    ),
)
@pytest.mark.anyio
def test_get_event(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_event_by_db(name))

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
        ("Lyon e-Sport", 200, "Deleted Event Lyon e-Sport", True),
        ("Lyon e-Sport 158", 404, "Event Lyon e-Sport 158 not found", False),
    ),
)
@pytest.mark.anyio
def test_delete_event(
    client: TestClient,
    event_loop: Generator,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_event_by_db(name))

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
        ("Lyon e-Sport1", {}, 404, "Event Lyon e-Sport1 not found", False),
        ("Lyon e-Sport1", {}, 200, "", True),
        ("Lyon e-Sport2", {"tournaments": [{"test": "Pro"}]}, 422, "", True),
        (
            "Lyon e-Sport2",
            {"tournaments": [{"name": "Pro"}, {"name": "Pro2"}]},
            200,
            "",
            True,
        ),
        (
            "Lyon e-Sport3",
            {"tournaments": [{"name": "Pro", "stages": [{"test": "Bracket"}]}]},
            422,
            "",
            True,
        ),
        (
            "Lyon e-Sport3",
            {
                "tournaments": [
                    {"name": "Pro", "stages": [{"name": "Bracket"}]},
                    {"name": "Pro2", "stages": [{"name": "Bracket"}]},
                ]
            },
            200,
            "",
            True,
        ),
    ),
)
@pytest.mark.anyio
def test_put_events(
    client: TestClient,
    event_loop: Generator,
    name: str,
    j_data: EventIn_Pydantic,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        event_loop.run_until_complete(create_event_by_db(name))

    response = client.put(f"{NAMESPACE}{name}", json=j_data)

    assert response.status_code == http_code

    data = response.json()
    if http_code == 200:
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message
