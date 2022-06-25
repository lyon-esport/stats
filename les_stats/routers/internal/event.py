from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from les_stats.schemas.internal.event import Event_Pydantic, EventIn_Pydantic
from les_stats.utils.status import Status

router = APIRouter()


@router.post("/", response_model=None)
async def add_event(event: Event_Pydantic):
    async with in_transaction("default") as connection:
        if not await Event.exists(name=event.name):
            event_obj = Event(**event.dict(exclude={"tournaments"}, exclude_unset=True))
            await event_obj.save(using_db=connection)
            if event.tournaments:
                for tournament in event.tournaments:
                    tournament_obj, _ = await Tournament.get_or_create(
                        **tournament.dict(exclude={"stages"}, exclude_unset=True),
                        using_db=connection,
                    )
                    await event_obj.tournaments.add(tournament_obj)
                    if tournament.stages:
                        for stage in tournament.stages:
                            stage_obj, _ = await Stage.get_or_create(
                                **stage.dict(exclude_unset=True), using_db=connection
                            )
                            await tournament_obj.stages.add(stage_obj)

            return Event_Pydantic.parse_obj(event_obj)
        else:
            raise HTTPException(
                status_code=409, detail=f"Event {event.name} already exist"
            )


@router.delete(
    "/{event_name}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
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
        Event_Pydantic.parse_obj(await Event.get(name=event_name))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Event {event_name} not found")

    async with in_transaction("default") as connection:
        event_obj = await Event.get(name=event_name)
        await event_obj.tournaments.clear(using_db=connection)
        if event.tournaments:
            for tournament in event.tournaments:
                tournament_obj, _ = await Tournament.get_or_create(
                    **tournament.dict(exclude={"stages"}, exclude_unset=True),
                    using_db=connection,
                )
                await event_obj.tournaments.add(tournament_obj)
                if tournament.stages:
                    for stage in tournament.stages:
                        stage_obj, _ = await Stage.get_or_create(
                            **stage.dict(exclude_unset=True), using_db=connection
                        )
                        await tournament_obj.stages.add(stage_obj)

        return Event_Pydantic.parse_obj(await Event.get(name=event_name))


@router.get(
    "/{event_name}",
    response_model=Event_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_event(event_name: str):
    try:
        event_obj = await Event.get(name=event_name)
        return Event_Pydantic.parse_obj(event_obj)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Event {event_name} not found")


@router.get("/", response_model=List[Event_Pydantic])
async def get_events():
    events_obj = await Event.all()
    return [Event_Pydantic.parse_obj(event_obj) for event_obj in events_obj]
