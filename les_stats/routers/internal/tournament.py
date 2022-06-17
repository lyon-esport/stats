from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from les_stats.models.tournament import Tournament
from les_stats.schemas.tournament import Tournament_Pydantic, TournamentIn_Pydantic
from les_stats.utils.status import Status

router = APIRouter()


@router.post("/", response_model=None)
async def add_tournament(tournament: TournamentIn_Pydantic):
    tournament_obj = await Tournament.create(**tournament.dict(exclude_unset=True))
    return await Tournament_Pydantic.from_tortoise_orm(tournament_obj)


@router.delete(
    "/{tournament_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}
)
async def delete_tournament(tournament_id: int):
    deleted_count = await Tournament.filter(id=tournament_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")
    return Status(message=f"Deleted Tournament {tournament_id}")


@router.put(
    "/{tournament_id}",
    response_model=Tournament_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_tournament(tournament_id: int, tournament: TournamentIn_Pydantic):
    try:
        await Tournament_Pydantic.from_queryset_single(Tournament.get(id=tournament_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")

    await Tournament.filter(id=tournament_id).update(**tournament.dict(exclude_unset=True))
    return await Tournament_Pydantic.from_queryset_single(Tournament.get(id=tournament_id))


@router.get(
    "/{tournament_id}",
    response_model=Tournament_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_tournament(tournament_id: int):
    try:
        return await Tournament_Pydantic.from_queryset_single(Tournament.get(id=tournament_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")


@router.get("/", response_model=List[Tournament_Pydantic])
async def get_tournaments():
    return await Tournament_Pydantic.from_queryset(Tournament.all())
