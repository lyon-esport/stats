from fastapi import APIRouter, Depends

from les_stats.routers.internal import api as internal_api
from les_stats.routers.lol import api as lol_api
from les_stats.routers.tft import api as tft_api
from les_stats.routers.valorant import api as valorant_api
from les_stats.utils.auth import verify_api_key
from les_stats.utils.config import get_settings

api_router = APIRouter(dependencies=[Depends(verify_api_key)])
api_router.include_router(internal_api.router, prefix="/internal")

if (
    get_settings().VALORANT_API_KEY is not None
    and get_settings().VALORANT_API_ROUTING is not None
):
    api_router.include_router(
        valorant_api.router, prefix="/valorant", tags=["valorant"]
    )

if (
    get_settings().TFT_API_KEY is not None
    and get_settings().TFT_API_ROUTING is not None
):
    api_router.include_router(tft_api.router, prefix="/tft", tags=["tft"])

if (
    get_settings().LOL_API_KEY is not None
    and get_settings().LOL_API_ROUTING is not None
):
    api_router.include_router(lol_api.router, prefix="/lol", tags=["lol"])
