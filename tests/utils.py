from les_stats.models.event import Event
from les_stats.schemas.event import Event_Pydantic


async def create_event_by_db(name: str):
    event_obj = await Event.create(name=name)
    await Event_Pydantic.from_tortoise_orm(event_obj)


async def update_event_by_db(id: int, name: str):
    event_obj = Event.filter(id=id).update(name=name)
    return event_obj
