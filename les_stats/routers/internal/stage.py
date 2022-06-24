from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from les_stats.models.internal.stage import Stage
from les_stats.schemas.internal.stage import Stage_Pydantic
from les_stats.utils.status import Status

router = APIRouter()


@router.post("/", response_model=None)
async def add_stage(stage: Stage_Pydantic):
    stage_obj = await Stage.create(**stage.dict(exclude_unset=True))
    return await Stage_Pydantic.from_tortoise_orm(stage_obj)


@router.delete(
    "/{stage_name}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}
)
async def delete_stage(stage_name: int):
    deleted_count = await Stage.filter(name=stage_name).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Stage {stage_name} not found")
    return Status(message=f"Deleted Stage {stage_name}")


@router.get(
    "/{stage_name}",
    response_model=Stage_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_stage(stage_name: str):
    try:
        return await Stage_Pydantic.from_queryset_single(Stage.get(name=stage_name))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Stage {stage_name} not found")


@router.get("/", response_model=List[Stage_Pydantic])
async def get_stages():
    return await Stage_Pydantic.from_queryset(Stage.all())
