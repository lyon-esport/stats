from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from les_stats.models.event import Event
from les_stats.schemas.event import Event_Pydantic, EventIn_Pydantic
from les_stats.utils.status import Status

router = APIRouter()


@router.post("/", response_model=None)
async def add_event(event: EventIn_Pydantic):
    event_obj = await Event.create(**event.dict(exclude_unset=True))
    return await Event_Pydantic.from_tortoise_orm(event_obj)


@router.delete(
    "/{event_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}
)
async def delete_event(event_id: int):
    deleted_count = await Event.filter(id=event_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return Status(message=f"Deleted Event {event_id}")


@router.put(
    "/{event_id}",
    response_model=Event_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_event(event_id: int, event: EventIn_Pydantic):
    try:
        await Event_Pydantic.from_queryset_single(Event.get(id=event_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    await Event.filter(id=event_id).update(**event.dict(exclude_unset=True))
    return await Event_Pydantic.from_queryset_single(Event.get(id=event_id))


@router.get(
    "/{event_id}",
    response_model=Event_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_event(event_id: int):
    try:
        return await Event_Pydantic.from_queryset_single(Event.get(id=event_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")


@router.get("/", response_model=List[Event_Pydantic])
async def get_events():
    return await Event_Pydantic.from_queryset(Event.all())
