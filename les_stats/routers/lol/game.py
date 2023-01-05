from typing import Dict

from fastapi import APIRouter, Request

from les_stats.models.internal.auth import Scope
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/", response_model=Dict[str, str])
@scope_required([Scope.read, Scope.write])
async def hello(request: Request):
    return {"hello": "world"}
