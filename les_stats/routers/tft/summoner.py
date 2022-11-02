from typing import List

from fastapi import APIRouter, Query, Request, Response

from les_stats.client_api.riot import RiotAPI
from les_stats.models.internal.auth import Scope
from les_stats.schemas.client_api.data import DataResponse
from les_stats.schemas.riot.game import RiotGame
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/by-puuid", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_summoners_name_from_puuid(
    request: Request, response: Response, encrypted_puuid: List[str] = Query()
):
    response.status_code, data = await RiotAPI(RiotGame.tft).get_summoners_name(
        encrypted_puuid
    )
    return data


@router.get("/by-name", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_summoners_puuid_from_name(
    request: Request, response: Response, summoner_name: List[str] = Query()
):
    response.status_code, data = await RiotAPI(RiotGame.tft).get_summoners_puuid(
        summoner_name
    )
    return data


@router.get("/rank", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_summoners_rank(
    request: Request, response: Response, summoner_id: List[str] = Query()
):
    response.status_code, data = await RiotAPI(RiotGame.tft).get_summoners_rank(
        summoner_id
    )
    return data
