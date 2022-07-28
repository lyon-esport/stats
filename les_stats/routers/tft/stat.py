from typing import List

from fastapi import APIRouter, Request, Response

from les_stats.models.internal.auth import Scope
from les_stats.schemas.client_api.data import DataResponse
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/tier-list/composition", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_tier_list_composition(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/tier-list/items", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_tier_list_item(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/tier-list/unit", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_tier_list_unit(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/player/rank", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_player_rank(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/player/position", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_player_position(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/player/kill", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_player_kill(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/games/damage", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_games_damage(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/games/time", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_games_time(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/games/round_death", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_games_round_death(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/game/ranking_damage", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_game_ranking_damage(
    request: Request,
    response: Response,
):
    return DataResponse()
