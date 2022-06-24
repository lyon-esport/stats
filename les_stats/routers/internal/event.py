from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from les_stats.models.internal.event import Event
from les_stats.models.internal.tournament import Tournament
from les_stats.models.internal.stage import Stage
from les_stats.schemas.internal.event import Event_Pydantic, EventIn_Pydantic
from les_stats.utils.status import Status

router = APIRouter()


@router.post("/", response_model=None)
async def add_event(event: Event_Pydantic):
    if not Event.filter(name=event.name).exists():
        event_obj = await Event.create(**event.dict(exclude={"tournaments"}, exclude_unset=True))
        for tournament in event.tournaments:
            tournament_obj, _ = await Tournament.get_or_create(**tournament.dict(exclude={"stages"}, exclude_unset=True))
            await event_obj.tournaments.add(tournament_obj)
            for stage in tournament.stages:
                stage_obj, _ = await Stage.get_or_create(**stage.dict(exclude_unset=True))
                await tournament_obj.stages.add(stage_obj)

        return await Event_Pydantic.from_tortoise_orm(event_obj)
    else:
        raise HTTPException(status_code=409, detail=f"Event {event.name} already exist")


@router.delete(
    "/{event_name}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}
)
async def delete_event(event_name: str):
    deleted_count = await Event.filter(name=event_name).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Event {event_name} not found")
    return Status(message=f"Deleted Event {event_name}")


@router.put(
    "/{event_name}",
    response_model=Event_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_event(event_name: str, event: EventIn_Pydantic):
    try:
        await Event_Pydantic.from_queryset_single(Event.get(name=event_name))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Event {event_name} not found")

    await Event.filter(name=event_name).update(**event.dict(exclude_unset=True))
    return await Event_Pydantic.from_queryset_single(Event.get(name=event_name))


@router.get(
    "/{event_name}",
    response_model=Event_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_event(event_name: str):
    try:
        return await Event_Pydantic.from_queryset_single(Event.get(name=event_name))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Event {event_name} not found")


@router.get("/", response_model=List[Event_Pydantic])
async def get_events():
    return await Event_Pydantic.from_queryset(Event.all())
