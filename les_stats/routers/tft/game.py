from typing import List

from fastapi import APIRouter, Query, Request, Response

from les_stats.client_api.riot import RiotAPI
from les_stats.models.internal.auth import Scope
from les_stats.schemas.client_api.data import DataResponse
from les_stats.schemas.riot.game import GameSaveIn_Pydantic, RiotGame, RiotHost
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/match-list/", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_matches_list_from_summoners(
    request: Request,
    response: Response,
    host: RiotHost,
    start: int = 0,
    end_time: int = None,
    start_time: int = None,
    count: int = 20,
    puuid: List[str] = Query(),
):
    response.status_code, data = await RiotAPI(RiotGame.tft).get_matches_list(
        puuid, host, start, end_time, start_time, count
    )
    return data


@router.get("/matches/", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_matches_stat_from_a_list_of_game(
    request: Request, response: Response, match_id: List[str] = Query()
):
    response.status_code, data = await RiotAPI(RiotGame.tft).get_matches(match_id)
    return data


@router.post("/matches/save/", response_model=List[DataResponse])
@scope_required([Scope.write])
async def save_matches_in_stat_system(
    request: Request, response: Response, matches_id: List[GameSaveIn_Pydantic]
):
    response.status_code, data = await RiotAPI(RiotGame.tft).save_tft_games(matches_id)
    return data


@router.put("/matches/save/", response_model=List[DataResponse])
@scope_required([Scope.write])
async def update_matches_in_stat_system(
    request: Request, response: Response, matches_id: List[GameSaveIn_Pydantic]
):
    response.status_code, data = await RiotAPI(RiotGame.tft).update_tft_games(
        matches_id
    )
    return data


@router.delete("/matches/save/", response_model=List[DataResponse])
@scope_required([Scope.write])
async def delete_matches_in_stat_system(
    request: Request, response: Response, matches_id: List[str]
):
    response.status_code, data = await RiotAPI(RiotGame.tft).delete_tft_games(
        matches_id
    )
    return data
