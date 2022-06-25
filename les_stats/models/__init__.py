from tortoise import Tortoise

from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament

Tortoise.init_models(["les_stats.models"], "models")
