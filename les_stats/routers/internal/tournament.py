from typing import List

from fastapi import APIRouter, HTTPException, Request, Response
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from les_stats.metrics.internal.metrics import metric_stage, metric_tournament
from les_stats.models.internal.auth import Scope
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from les_stats.schemas.internal.tournament import (
    Tournament_Pydantic,
    TournamentIn_Pydantic,
)
from les_stats.utils.auth import scope_required
from les_stats.utils.status import Status

router = APIRouter()


@router.post(
    "",
    response_model=Tournament_Pydantic,
)
@scope_required([Scope.write])
async def add_tournament(
    request: Request, response: Response, tournament: Tournament_Pydantic
):
    async with in_transaction("default") as connection:
        if not await Tournament.exists(name=tournament.name):
            tournament_obj = Tournament(
                **tournament.dict(exclude={"stages"}, exclude_unset=True)
            )
            await tournament_obj.save(using_db=connection)
            if tournament.stages:
                for stage in tournament.stages:
                    stage_obj, _ = await Stage.get_or_create(
                        **stage.dict(exclude_unset=True), using_db=connection
                    )
                    await tournament_obj.stages.add(stage_obj)
        else:
            raise HTTPException(
                status_code=409, detail=f"Tournament {tournament.name} already exist"
            )
    metric_tournament.inc()
    metric_stage.inc(await Stage.all().count())
    response.status_code = 201
    return Tournament_Pydantic.parse_obj(tournament_obj)


@router.delete(
    "/{tournament_name}",
    response_model=Status,
)
@scope_required([Scope.write])
async def delete_tournament(request: Request, tournament_name: str):
    deleted_count = await Tournament.filter(name=tournament_name).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404, detail=f"Tournament {tournament_name} not found"
        )
    metric_tournament.dec()
    return Status(message=f"Deleted Tournament {tournament_name}")


@router.put(
    "/{tournament_name}",
    response_model=Tournament_Pydantic,
)
@scope_required([Scope.write])
async def update_tournament(
    request: Request, tournament_name: str, tournament: TournamentIn_Pydantic
):
    try:
        Tournament_Pydantic.parse_obj(await Tournament.get(name=tournament_name))
    except DoesNotExist:
        raise HTTPException(
            status_code=404, detail=f"Tournament {tournament_name} not found"
        )

    async with in_transaction("default") as connection:
        tournament_obj = await Tournament.get(name=tournament_name)
        await tournament_obj.stages.clear(using_db=connection)
        if tournament.stages:
            for stage in tournament.stages:
                stage_obj, _ = await Stage.get_or_create(
                    **stage.dict(exclude_unset=True), using_db=connection
                )
                await tournament_obj.stages.add(stage_obj)

    return Tournament_Pydantic.parse_obj(await Tournament.get(name=tournament_name))


@router.get(
    "/{tournament_name}",
    response_model=Tournament_Pydantic,
)
@scope_required([Scope.read, Scope.write])
async def get_tournament(request: Request, tournament_name: str):
    try:
        tournament_obj = await Tournament.get(name=tournament_name)
        return Tournament_Pydantic.parse_obj(tournament_obj)
    except DoesNotExist:
        raise HTTPException(
            status_code=404, detail=f"Tournament {tournament_name} not found"
        )


@router.get("", response_model=List[Tournament_Pydantic])
@scope_required([Scope.read, Scope.write])
async def get_tournaments(request: Request):
    tournaments_obj = await Tournament.all()
    return [
        Tournament_Pydantic.parse_obj(tournament_obj)
        for tournament_obj in tournaments_obj
    ]
