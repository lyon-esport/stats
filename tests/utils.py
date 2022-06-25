from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament


async def create_event_by_db(name: str):
    await Event.create(name=name)


async def create_tournament_by_db(name: str):
    await Tournament.create(name=name)


async def create_stage_by_db(name: str):
    await Stage.create(name=name)
