from tortoise import Tortoise

from les_stats.models.internal.auth import Api
from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from les_stats.models.lol.game import LolGame
from les_stats.models.tft.game import (
    TFTAugment,
    TFTCompanion,
    TFTCurrentTrait,
    TFTCurrentUnit,
    TFTGame,
    TFTItem,
    TFTParticipant,
    TFTPlayer,
    TFTTrait,
    TFTUnit,
)
from les_stats.models.valorant.game import ValorantGame

Tortoise.init_models(["les_stats.models"], "models")
