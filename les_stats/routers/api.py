from fastapi import APIRouter

from les_stats.routers.internal import api as internal_api
from les_stats.routers.valorant import api as valorant_api

api_router = APIRouter()
api_router.include_router(internal_api.router, prefix="/internal", tags=["internal"])
api_router.include_router(valorant_api.router, prefix="/valorant", tags=["valorant"])
