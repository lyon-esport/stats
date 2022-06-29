from typing import Dict

from fastapi import APIRouter, Request

from les_stats.client_api.riot import RiotAPI, RiotGame
from les_stats.models.internal.auth import Scope
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/", response_model=Dict[str, str])
@scope_required([Scope.read, Scope.write])
async def hello(request: Request):
    print(await RiotAPI(RiotGame.lol).test())
    return {"hello": "world"}
