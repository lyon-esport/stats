from typing import List, Optional, Union, Dict

from fastapi import APIRouter, Request, Response
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
from tortoise.functions import Avg as TAvg
from tortoise.functions import Count as TCount
from tortoise.functions import Max as TMax
from tortoise.functions import Min as TMin
from tortoise.functions import Sum as TSum

from les_stats.models.internal.auth import Scope
from les_stats.models.tft.game import TFTGame, TFTItem, TFTPlayer, TFTTrait, TFTUnit
from les_stats.schemas.client_api.data import ErrorResponse
from les_stats.schemas.internal.generic import GameTimeElapsed
from ...models.valorant.game import ValorantWeapon, ValorantDamageRoundStat
import logging

from les_stats.utils.auth import scope_required

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(
    "/tier-list/weapons",
    response_model=Dict[str, List[dict]],
)
@scope_required([Scope.read, Scope.write])
async def get_tier_list_weapons(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    # weapons = await ValorantWeapon.all().annotate(
    #     ""
    # )

    payload = {}

    # Kill
    sql = """SELECT COALESCE(wp.name, v.last_hit_damage_item) as name , count(*) as kill from valorantweapon as wp 
    LEFT join valorantplayerroundkill v on wp.id = v.last_hit_damage_item
    group by wp.name
    ORDER BY 2 DESC;

    """
    # Need to get a connection. Unless explicitly specified, the name should be 'default'
    conn = Tortoise.get_connection("default")
    res = await conn.execute_query_dict(sql)
    weapons_stats = []
    for weapon in res:
        weapons_stats.append(weapon)
    payload["kills"] = weapons_stats

    # Damages
    sql = """SELECT wp.name, count(*) as kill from valorantweapon as wp 
   inner join valorantplayerroundstat v on wp.id = v.weapon_id
    group by wp.name
    ORDER BY 2 DESC;

    """
    # Need to get a connection. Unless explicitly specified, the name should be 'default'
    conn = Tortoise.get_connection("default")
    res = await conn.execute_query_dict(sql)
    weapons_stats = []
    for weapon in res:
        weapons_stats.append(weapon)
    payload["buys"] = weapons_stats

    # Buy


    return payload
