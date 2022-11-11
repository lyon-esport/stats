from fastapi import APIRouter

from les_stats.routers.valorant import game, player, stat

router = APIRouter()
router.include_router(game.router, prefix="/game")
router.include_router(player.router, prefix="/player")
router.include_router(stat.router, prefix="/stats")
