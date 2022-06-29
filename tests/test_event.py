import pytest

from les_stats.models.internal.auth import Scope
from les_stats.models.internal.event import Event
from les_stats.schemas.internal.event import Event_Pydantic, EventIn_Pydantic
from tests.utils import CustomClient

NAMESPACE = "/internal/event/"


@pytest.mark.asyncio
async def test_post_event_scopes(client: CustomClient):
    await client.test_api_scope(
        "POST", f"{NAMESPACE}", [Scope.write], json={"name": "test"}
    )


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
@pytest.mark.asyncio
async def test_post_event(
    client: CustomClient,
    j_data: Event_Pydantic,
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


@pytest.mark.asyncio
async def test_get_events_scopes(client: CustomClient):
    await client.test_api_scope("GET", f"{NAMESPACE}", [Scope.read, Scope.write])


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
@pytest.mark.asyncio
async def test_get_events(client: CustomClient, name: str, http_code: int):
    await Event.create(name=name)

    response = await client.test_api("GET", f"{NAMESPACE}", Scope.read)

    assert response.status_code == http_code
    data = response.json()
    assert data[0]["name"] == name


@pytest.mark.asyncio
async def test_get_tournament_scopes(client: CustomClient):
    await client.test_api_scope("GET", f"{NAMESPACE}test", [Scope.read, Scope.write])


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
@pytest.mark.asyncio
async def test_get_event(
    client: CustomClient,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Event.create(name=name)

    response = await client.test_api("GET", f"{NAMESPACE}{name}", Scope.read)

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message


@pytest.mark.asyncio
async def test_delete_event_scopes(client: CustomClient):
    await client.test_api_scope("DELETE", f"{NAMESPACE}test", [Scope.write])


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
@pytest.mark.asyncio
async def test_delete_event(
    client: CustomClient,
    name: str,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Event.create(name=name)

    response = await client.test_api("DELETE", f"{NAMESPACE}{name}", Scope.write)

    assert response.status_code == http_code
    data = response.json()
    if http_code == 200:
        assert data["message"] == message
    elif http_code == 404:
        assert data["detail"] == message


@pytest.mark.asyncio
async def test_put_event_scopes(client: CustomClient):
    await client.test_api_scope("PUT", f"{NAMESPACE}test", [Scope.write], json={})


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
@pytest.mark.asyncio
async def test_put_events(
    client: CustomClient,
    name: str,
    j_data: EventIn_Pydantic,
    http_code: int,
    message: str,
    create: bool,
):
    if create:
        await Event.create(name=name)

    response = await client.test_api(
        "PUT", f"{NAMESPACE}{name}", Scope.write, json=j_data
    )

    assert response.status_code == http_code

    data = response.json()
    if http_code == 200:
        assert data["name"] == name
    elif http_code == 404:
        assert data["detail"] == message
