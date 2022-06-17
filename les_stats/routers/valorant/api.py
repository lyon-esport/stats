from fastapi import APIRouter

from les_stats.routers.valorant import game

router = APIRouter()
router.include_router(game.router, prefix="/game")
