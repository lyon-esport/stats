from les_stats.models.event import Event
from les_stats.schemas.event import Event_Pydantic
from les_stats.models.tournament import Tournament
from les_stats.schemas.tournament import Tournament_Pydantic
from les_stats.models.stage import Stage
from les_stats.schemas.stage import Stage_Pydantic


async def create_event_by_db(name: str):
    event_obj = await Event.create(name=name)
    await Event_Pydantic.from_tortoise_orm(event_obj)


async def update_event_by_db(id: int, name: str):
    event_obj = Event.filter(id=id).update(name=name)
    return event_obj


async def create_tournament_by_db(name: str):
    tournament_obj = await Tournament.create(name=name)
    await Tournament_Pydantic.from_tortoise_orm(tournament_obj)


async def update_tournament_by_db(id: int, name: str):
    tournament_obj = Tournament.filter(id=id).update(name=name)
    return tournament_obj


async def create_stage_by_db(name: str):
    stage_obj = await Stage.create(name=name)
    await Stage_Pydantic.from_tortoise_orm(stage_obj)


async def update_stage_by_db(id: int, name: str):
    stage_obj = Stage.filter(id=id).update(name=name)
    return stage_obj
