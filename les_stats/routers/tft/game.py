from typing import List, Optional

from fastapi import APIRouter, Query, Request, Response
from tortoise.exceptions import DoesNotExist

from les_stats.client_api.riot import RiotAPI
from les_stats.models.internal.auth import Scope
from les_stats.models.tft.game import TFTGame
from les_stats.schemas.client_api.data import DataResponse, ErrorResponse
from les_stats.schemas.riot.game import GameSaveIn_Pydantic, RiotGame
from les_stats.utils.auth import scope_required
from les_stats.utils.internal import generate_kwargs_structure

router = APIRouter()


@router.get("/match-list", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_matches_list_from_summoners(
    request: Request,
    response: Response,
    start: int = 0,
    end_time: int = None,
    start_time: int = None,
    count: int = 20,
    puuid: List[str] = Query(),
):
    response.status_code, data = await RiotAPI(RiotGame.tft).get_matches_list(
        puuid, start, end_time, start_time, count
    )
    return data


@router.get("/matches", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_matches_stat_from_a_list_of_game(
    request: Request, response: Response, match_id: List[str] = Query()
):
    response.status_code, data = await RiotAPI(RiotGame.tft).get_matches(match_id)
    return data


@router.get("/matches/save", response_model=DataResponse)
@scope_required([Scope.read, Scope.write])
async def get_matches_in_stat_system(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        games = (
            await TFTGame.all()
            .filter(**generate_kwargs_structure(event, tournament, stage))
            .values("match_id")
        )

        if len(games) == 0:
            raise DoesNotExist

        data = DataResponse(data=games)
    except DoesNotExist:
        response.status_code = 200
        return DataResponse(
            error=ErrorResponse(
                status_code=200, message="No games found in stat system"
            )
        )

    return data


@router.post("/matches/save", response_model=List[DataResponse])
@scope_required([Scope.write])
async def save_matches_in_stat_system(
    request: Request, response: Response, matches_id: List[GameSaveIn_Pydantic]
):
    response.status_code, data = await RiotAPI(RiotGame.tft).save_tft_games(matches_id)
    return data


@router.put("/matches/save", response_model=List[DataResponse])
@scope_required([Scope.write])
async def update_matches_in_stat_system(
    request: Request, response: Response, matches_id: List[GameSaveIn_Pydantic]
):
    response.status_code, data = await RiotAPI(RiotGame.tft).update_tft_games(
        matches_id
    )
    return data


@router.delete("/matches/save", response_model=List[DataResponse])
@scope_required([Scope.write])
async def delete_matches_in_stat_system(
    request: Request, response: Response, matches_id: List[str]
):
    response.status_code, data = await RiotAPI(RiotGame.tft).delete_tft_games(
        matches_id
    )
    return data
