import pytest

from les_stats.models.internal.auth import Scope
from tests.utils import CustomClient

NAMESPACE = "/tft/stat/"


@pytest.mark.asyncio
async def test_get_tier_list_composition_scopes(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}tier-list/composition", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_tier_list_item(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}tier-list/item", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_tier_list_unit(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}tier-list/unit", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_player_placement(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}player/placement", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_player_kill(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}player/kill", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_games_death_round(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}player/death_round", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_games_damage(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}games/damage", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_games_time(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}games/time", [Scope.read, Scope.write]
    )


@pytest.mark.asyncio
async def test_get_game_ranking_damage(client: CustomClient):
    await client.test_api_scope(
        "GET", f"{NAMESPACE}game/ranking/damage", [Scope.read, Scope.write]
    )
