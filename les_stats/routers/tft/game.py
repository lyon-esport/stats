from typing import List

from fastapi import APIRouter, Query, Request

from les_stats.client_api.riot import RiotAPI, RiotGame, RiotHost
from les_stats.models.internal.auth import Scope
from les_stats.schemas.client_api.data import DataResponse
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/match-list/{puuid}", response_model=DataResponse)
@scope_required([Scope.read, Scope.write])
async def get_match_list_from_a_summoner(
    request: Request,
    puuid: str,
    host: RiotHost,
    start: int = 0,
    end_time: int = None,
    start_time: int = None,
    count: int = 20,
):
    return await RiotAPI(RiotGame.tft).get_match_list(
        puuid, host, start, end_time, start_time, count
    )


@router.get("/matches/", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_matches_stat_from_a_list_of_game(
    request: Request, matches_id: List[str] = Query(None)
):
    return await RiotAPI(RiotGame.tft).get_matches(matches_id)


@router.post("/matches/save", response_model=List[DataResponse])
@scope_required([Scope.write])
async def save_matches_in_stat_system(request: Request, matches_id: List[str]):
    return await RiotAPI(RiotGame.tft).save_tft_games(matches_id)


@router.delete("/matches/save", response_model=List[DataResponse])
@scope_required([Scope.write])
async def delete_matches_in_stat_system(request: Request, matches_id: List[str]):
    return await RiotAPI(RiotGame.tft).delete_tft_games(matches_id)
