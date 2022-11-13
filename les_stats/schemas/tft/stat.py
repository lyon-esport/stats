from typing import List, Optional

from pydantic import BaseModel

from les_stats.schemas.client_api.data import ErrorResponse
from les_stats.schemas.internal.generic import TimeElapsed


class TierListComposition(BaseModel):
    name: str
    count: int


class TierListCompositionTier(BaseModel):
    min: TierListComposition
    max: TierListComposition


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
    id: int
    name: str
    count: int


class TierListItemRanks(BaseModel):
    min: TierListItem
    max: TierListItem


class TierListItemResponse(BaseModel):
    data: TierListItemRanks = None
    error: ErrorResponse = None


class TierListUnit(BaseModel):
    character_id: str
    count: int


class TierListUnitTier(BaseModel):
    min: TierListUnit
    max: TierListUnit


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


class GamesDamage(BaseModel):
    puuid: str
    damage: int


class GamesDamageRanks(BaseModel):
    min: GamesDamage
    avg: float
    max: GamesDamage
    sum: int


class GamesDamageResponse(BaseModel):
    data: GamesDamageRanks = None
    error: ErrorResponse = None


class GamesTime(BaseModel):
    min_time: TimeElapsed
    avg_time: TimeElapsed
    max_time: TimeElapsed
    sum_time: TimeElapsed


class GamesTimeResponse(BaseModel):
    data: GamesTime = None
    error: ErrorResponse = None


class GameDamage(BaseModel):
    puuid: str
    damage: int


class GameDamageResponse(BaseModel):
    data: List[GameDamage] = None
    error: ErrorResponse = None
