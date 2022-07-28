from fastapi import APIRouter

from les_stats.routers.tft import game, stat, summoner

router = APIRouter()
router.include_router(summoner.router, prefix="/summoner")
router.include_router(game.router, prefix="/game")
router.include_router(stat.router, prefix="/stat")
