from typing import List

from fastapi import APIRouter, Query, Request, Response
from pyot.core.queue import Queue
from pyot.models import val

from les_stats.models.internal.auth import Scope
from les_stats.routers.valorant.utils import insert_match_data
from les_stats.schemas.client_api.data import DataResponse, ErrorResponse
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/match-list", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_matches_list_from_summoner(
    request: Request,
    response: Response,
    start: int = 0,
    end_time: int = None,
    start_time: int = None,
    count: int = 20,
    puuid: str = Query(),
):

    history = await val.MatchHistory(puuid=puuid).get()
    async with Queue() as queue:
        for match in history.history[start:count]:
            await queue.put(match.get())
        matches: List[val.Match] = await queue.join()

    data = []
    for match in matches:
        data.append(DataResponse(data=match.id))
    return data


@router.get("/matches", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_matches_stat_from_a_list_of_game(
    request: Request, response: Response, match_ids: List[str] = Query()
):
    async with Queue() as queue:
        for match_id in match_ids:
            await queue.put(val.Match(match_id).get())
        matches: List[val.Match] = await queue.join()
    data = []
    for match in matches:
        DataResponse(data=match.dict())
    return data


@router.post("/matches/save", response_model=List[DataResponse])
@scope_required([Scope.write])
async def save_matches_in_stat_system(
    request: Request, response: Response, match_ids: List[str]
):
    async with Queue() as queue:
        for match_id in match_ids:
            await queue.put(val.Match(match_id).get())
        matches: List[val.Match] = await queue.join()
    data = []
    for match in matches:
        error = None
        result = await insert_match_data(match)
        if result:
            error = ErrorResponse(status_code=100, message=result)
        data.append(DataResponse(data=match.id, error=error))
    return data


@router.put("/matches/save", response_model=List[DataResponse])
@scope_required([Scope.write])
async def update_matches_in_stat_system(
    request: Request, response: Response, matches_id: List[str]
):
    return await save_matches_in_stat_system(request, response, matches_id)
