from typing import Optional

from pydantic import BaseModel

from les_stats.schemas.client_api.data import ErrorResponse
from les_stats.schemas.internal.generic import GameTimeElapsed


class DeathRound(BaseModel):
    puuid: str
    name: Optional[str] = ""
    min: int
    max: int
    average: float


class DeathRoundResponse(BaseModel):
    data: DeathRound = None
    error: ErrorResponse = None


class GameTime(BaseModel):
    min_time: GameTimeElapsed
    avg_time: GameTimeElapsed
    max_time: GameTimeElapsed


class GameTimeResponse(BaseModel):
    data: GameTime = None
    error: ErrorResponse = None


class RankingDamage(BaseModel):
    puuid: str
    name: Optional[str] = ""
    damage: int


class RankingDamageResponse(BaseModel):
    data: RankingDamage = None
    error: ErrorResponse = None
