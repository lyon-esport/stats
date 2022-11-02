from typing import Optional

from pydantic import BaseModel

from les_stats.schemas.client_api.data import ErrorResponse
from les_stats.schemas.internal.generic import GameTimeElapsed


class TierListComposition(BaseModel):
    name: str
    count: int


class TierListCompositionTier(BaseModel):
    min: TierListComposition
    max: TierListComposition
    sum: int


class TierListCompositionRanks(BaseModel):
    tier1: Optional[TierListCompositionTier] = None
    tier2: Optional[TierListCompositionTier] = None
    tier3: Optional[TierListCompositionTier] = None
    tier4: Optional[TierListCompositionTier] = None
    tier5: Optional[TierListCompositionTier] = None
    tier6: Optional[TierListCompositionTier] = None
    tier7: Optional[TierListCompositionTier] = None
    tier8: Optional[TierListCompositionTier] = None
    tier9: Optional[TierListCompositionTier] = None
    tier10: Optional[TierListCompositionTier] = None
    tier11: Optional[TierListCompositionTier] = None
    tier12: Optional[TierListCompositionTier] = None


class TierListCompositionResponse(BaseModel):
    data: TierListCompositionRanks = None
    error: ErrorResponse = None


class TierListItem(BaseModel):
    name: str
    count: int


class TierListItemRanks(BaseModel):
    min: TierListItem
    avg: int
    max: TierListItem
    sum: int


class TierListItemResponse(BaseModel):
    data: TierListItemRanks = None
    error: ErrorResponse = None


class TierListUnit(BaseModel):
    character_id: str
    count: int


class TierListUnitTier(BaseModel):
    min: TierListUnit
    max: TierListUnit
    sum: int


class TierListUnitRanks(BaseModel):
    tier1: Optional[TierListUnitTier] = None
    tier2: Optional[TierListUnitTier] = None
    tier3: Optional[TierListUnitTier] = None


class TierListUnitResponse(BaseModel):
    data: TierListUnitRanks = None
    error: ErrorResponse = None


class PlayerPlacement(BaseModel):
    min: int
    avg: float
    max: int


class PlayerPlacementResponse(BaseModel):
    data: PlayerPlacement = None
    error: ErrorResponse = None


class PlayerKill(BaseModel):
    min: int
    avg: float
    max: int
    sum: int


class PlayerKillResponse(BaseModel):
    data: PlayerKill = None
    error: ErrorResponse = None


class DeathRound(BaseModel):
    min: int
    avg: float
    max: int


class DeathRoundResponse(BaseModel):
    data: DeathRound = None
    error: ErrorResponse = None


class GameDamage(BaseModel):
    puuid: str
    damage: int


class GameDamageRanks(BaseModel):
    min: GameDamage
    avg: int
    max: GameDamage
    sum: int


class GameDamageResponse(BaseModel):
    data: GameDamageRanks = None
    error: ErrorResponse = None


class GameTime(BaseModel):
    min_time: GameTimeElapsed
    avg_time: GameTimeElapsed
    max_time: GameTimeElapsed
    sum_time: GameTimeElapsed


class GameTimeResponse(BaseModel):
    data: GameTime = None
    error: ErrorResponse = None


class RankingDamage(BaseModel):
    puuid: str
    damage: int


class RankingDamageResponse(BaseModel):
    data: RankingDamage = None
    error: ErrorResponse = None
