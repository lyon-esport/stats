from fastapi import APIRouter

from les_stats.routers.lol import game

router = APIRouter()
router.include_router(game.router, prefix="/game")
