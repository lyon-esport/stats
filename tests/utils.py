from les_stats.models.internal.event import Event
from les_stats.schemas.internal.event import Event_Pydantic
from les_stats.models.internal.tournament import Tournament
from les_stats.schemas.internal.tournament import Tournament_Pydantic
from les_stats.models.internal.stage import Stage
from les_stats.schemas.internal.stage import Stage_Pydantic


async def create_event_by_db(name: str):
    await Event.create(name=name)


async def update_event_by_db(name: str):
    event_obj = Event.filter(name=name).update(name=name)
    return event_obj


async def create_tournament_by_db(name: str):
    await Tournament.create(name=name)


async def update_tournament_by_db(name: str):
    tournament_obj = Tournament.filter(name=name).update(name=name)
    return tournament_obj


async def create_stage_by_db(name: str):
    await Stage.create(name=name)
