from fastapi import APIRouter, Depends

from les_stats.routers.internal import api as internal_api
from les_stats.routers.lol import api as lol_api
from les_stats.routers.valorant import api as valorant_api
from les_stats.utils.auth import verify_api_key

api_router = APIRouter(dependencies=[Depends(verify_api_key)])
api_router.include_router(internal_api.router, prefix="/internal")
api_router.include_router(lol_api.router, prefix="/lol", tags=["lol"])
api_router.include_router(valorant_api.router, prefix="/valorant", tags=["valorant"])
