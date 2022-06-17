from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from les_stats.models.stage import Stage
from les_stats.schemas.stage import Stage_Pydantic, StageIn_Pydantic
from les_stats.utils.status import Status

router = APIRouter()


@router.post("/", response_model=None)
async def add_stage(stage: StageIn_Pydantic):
    stage_obj = await Stage.create(**stage.dict(exclude_unset=True))
    return await Stage_Pydantic.from_tortoise_orm(stage_obj)


@router.delete(
    "/{stage_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}
)
async def delete_stage(stage_id: int):
    deleted_count = await Stage.filter(id=stage_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Stage {stage_id} not found")
    return Status(message=f"Deleted Stage {stage_id}")


@router.put(
    "/{stage_id}",
    response_model=Stage_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_stage(stage_id: int, stage: StageIn_Pydantic):
    try:
        await Stage_Pydantic.from_queryset_single(Stage.get(id=stage_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Stage {stage_id} not found")

    await Stage.filter(id=stage_id).update(**stage.dict(exclude_unset=True))
    return await Stage_Pydantic.from_queryset_single(Stage.get(id=stage_id))


@router.get(
    "/{stage_id}",
    response_model=Stage_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_stage(stage_id: int):
    try:
        return await Stage_Pydantic.from_queryset_single(Stage.get(id=stage_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Stage {stage_id} not found")


@router.get("/", response_model=List[Stage_Pydantic])
async def get_stages():
    return await Stage_Pydantic.from_queryset(Stage.all())
