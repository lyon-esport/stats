from fastapi import APIRouter

from les_stats.routers.internal import event, stage, tournament

router = APIRouter()
router.include_router(event.router, prefix="/event", tags=["event"])
router.include_router(tournament.router, prefix="/tournament", tags=["tournament"])
router.include_router(stage.router, prefix="/stage", tags=["stage"])
