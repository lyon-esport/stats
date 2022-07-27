from typing import List

from fastapi import APIRouter, Query, Request

from les_stats.client_api.riot import RiotAPI, RiotGame
from les_stats.models.internal.auth import Scope
from les_stats.schemas.client_api.data import DataResponse
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/by-puuid/", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_summoners_name_from_puuid(
    request: Request, encrypted_puuids: List[str] = Query(None)
):
    return await RiotAPI(RiotGame.tft).get_summoners_name(encrypted_puuids)


@router.get("/by-name/", response_model=List[DataResponse])
@scope_required([Scope.read, Scope.write])
async def get_summoners_puuid_from_name(
    request: Request, summoners_name: List[str] = Query(None)
):
    return await RiotAPI(RiotGame.tft).get_summoners_puuid(summoners_name)
