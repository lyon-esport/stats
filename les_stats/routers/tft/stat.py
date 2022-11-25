from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from tortoise.exceptions import DoesNotExist
from tortoise.functions import Avg as TAvg
from tortoise.functions import Count as TCount
from tortoise.functions import Max as TMax
from tortoise.functions import Min as TMin
from tortoise.functions import Sum as TSum

from les_stats.models.internal.auth import Scope
from les_stats.models.tft.game import TFTGame, TFTItem, TFTPlayer, TFTTrait, TFTUnit
from les_stats.schemas.client_api.data import ErrorResponse
from les_stats.schemas.internal.generic import TimeElapsed
from les_stats.schemas.riot.game import RiotHost
from les_stats.schemas.tft.stat import (
    DeathRound,
    DeathRoundResponse,
    GameDamage,
    GameDamageResponse,
    GamesDamage,
    GamesDamageRanks,
    GamesDamageResponse,
    GamesTime,
    GamesTimeResponse,
    PlayerKill,
    PlayerKillResponse,
    PlayerPlacement,
    PlayerPlacementResponse,
    TierListComposition,
    TierListCompositionRanks,
    TierListCompositionResponse,
    TierListCompositionTier,
    TierListItem,
    TierListItemRanks,
    TierListItemResponse,
    TierListUnit,
    TierListUnitRanks,
    TierListUnitResponse,
    TierListUnitTier,
)
from les_stats.utils.auth import scope_required
from les_stats.utils.internal import generate_kwargs_structure

router = APIRouter()


@router.get(
    "/tier-list/composition",
    response_model=TierListCompositionResponse,
)
@scope_required([Scope.read, Scope.write])
async def get_tier_list_composition(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        traits = (
            await TFTTrait.all()
            .prefetch_related(
                "current_trait",
            )
            .filter(
                current_trait__tier_current__gt=0,
                **generate_kwargs_structure(
                    event,
                    tournament,
                    stage,
                    prefix="current_trait__participant__game__",
                ),
            )
            .group_by("name", "current_trait__tier_current")
            .annotate(
                count_tier_list_trait=TCount("current_trait__tier_current"),
            )
            .values("name", "current_trait__tier_current", "count_tier_list_trait")
        )

        if len(traits) == 0:
            raise DoesNotExist

        tiers = {}

        for trait in traits:
            if f"tier{trait['current_trait__tier_current']}" not in tiers:
                tiers[f"tier{trait['current_trait__tier_current']}"] = {
                    "min": {
                        "name": trait["name"],
                        "count": trait["count_tier_list_trait"],
                    },
                    "max": {
                        "name": trait["name"],
                        "count": trait["count_tier_list_trait"],
                    },
                }
            else:

                if (
                    tiers[f"tier{trait['current_trait__tier_current']}"]["min"]["count"]
                    > trait["count_tier_list_trait"]
                ):
                    tiers[f"tier{trait['current_trait__tier_current']}"]["min"][
                        "name"
                    ] = trait["name"]
                    tiers[f"tier{trait['current_trait__tier_current']}"]["min"][
                        "count"
                    ] = trait["count_tier_list_trait"]

                if (
                    tiers[f"tier{trait['current_trait__tier_current']}"]["max"]["count"]
                    < trait["count_tier_list_trait"]
                ):
                    tiers[f"tier{trait['current_trait__tier_current']}"]["max"][
                        "name"
                    ] = trait["name"]
                    tiers[f"tier{trait['current_trait__tier_current']}"]["max"][
                        "count"
                    ] = trait["count_tier_list_trait"]

        for k in TierListCompositionRanks().dict().keys():
            if k in tiers:
                tiers[k] = TierListCompositionTier(
                    min=TierListComposition(
                        name=tiers[k]["min"]["name"],
                        count=tiers[k]["min"]["count"],
                    ),
                    max=TierListComposition(
                        name=tiers[k]["max"]["name"],
                        count=tiers[k]["max"]["count"],
                    ),
                )

        data = TierListCompositionResponse(data=TierListCompositionRanks(**tiers))
    except DoesNotExist:
        response.status_code = 200
        return TierListCompositionResponse(
            error=ErrorResponse(
                status_code=200, message="No games found in stat system"
            )
        )
    return data


@router.get("/tier-list/item", response_model=TierListItemResponse)
@scope_required([Scope.read, Scope.write])
async def get_tier_list_item(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        items = (
            await TFTItem.all()
            .prefetch_related("items")
            .filter(
                **generate_kwargs_structure(
                    event, tournament, stage, prefix="items__participant__game__"
                )
            )
            .exclude(items__id=None)
        )

        if len(items) == 0:
            raise DoesNotExist

        nb_items = await items[0].items.all().count()
        min = {"id": items[0].id, "name": items[0].name, "count": nb_items}
        max = {"id": items[0].id, "name": items[0].name, "count": nb_items}

        for item in items:
            nb_items = await item.items.all().count()

            if min["count"] > nb_items:
                min["id"] = item.id
                min["name"] = item.name
                min["count"] = nb_items

            if max["count"] < nb_items:
                max["id"] = item.id
                max["name"] = item.name
                max["count"] = nb_items

        data = TierListItemResponse(
            data=TierListItemRanks(
                min=TierListItem(
                    id=min["id"],
                    name=min["name"],
                    count=min["count"],
                ),
                max=TierListItem(
                    id=max["id"],
                    name=max["name"],
                    count=max["count"],
                ),
            )
        )
    except DoesNotExist:
        response.status_code = 200
        return TierListCompositionResponse(
            error=ErrorResponse(
                status_code=200, message="No games found in stat system"
            )
        )

    return data


@router.get("/tier-list/unit", response_model=TierListUnitResponse)
@scope_required([Scope.read, Scope.write])
async def get_tier_list_unit(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        units = (
            await TFTUnit.all()
            .prefetch_related(
                "current_unit",
            )
            .filter(
                **generate_kwargs_structure(
                    event, tournament, stage, prefix="current_unit__participant__game__"
                )
            )
            .exclude(current_unit=None)
            .group_by("character_id", "current_unit__tier")
            .annotate(
                count_tier_list_unit=TCount("current_unit__tier"),
            )
            .values("character_id", "current_unit__tier", "count_tier_list_unit")
        )

        if len(units) == 0:
            raise DoesNotExist

        tiers = {}

        for unit in units:
            if f"tier{unit['current_unit__tier']}" not in tiers:
                tiers[f"tier{unit['current_unit__tier']}"] = {
                    "min": {
                        "character_id": unit["character_id"],
                        "count": unit["count_tier_list_unit"],
                    },
                    "max": {
                        "character_id": unit["character_id"],
                        "count": unit["count_tier_list_unit"],
                    },
                    "total": unit["count_tier_list_unit"],
                }
            else:
                tiers[f"tier{unit['current_unit__tier']}"]["total"] += unit[
                    "count_tier_list_unit"
                ]

                if (
                    tiers[f"tier{unit['current_unit__tier']}"]["min"]["count"]
                    > unit["count_tier_list_unit"]
                ):
                    tiers[f"tier{unit['current_unit__tier']}"]["min"][
                        "character_id"
                    ] = unit["character_id"]
                    tiers[f"tier{unit['current_unit__tier']}"]["min"]["count"] = unit[
                        "count_tier_list_unit"
                    ]

                if (
                    tiers[f"tier{unit['current_unit__tier']}"]["max"]["count"]
                    < unit["count_tier_list_unit"]
                ):
                    tiers[f"tier{unit['current_unit__tier']}"]["max"][
                        "character_id"
                    ] = unit["character_id"]
                    tiers[f"tier{unit['current_unit__tier']}"]["max"]["count"] = unit[
                        "count_tier_list_unit"
                    ]

        for k in TierListUnitRanks().dict().keys():
            if k in tiers:
                tiers[k] = TierListUnitTier(
                    min=TierListUnit(
                        character_id=tiers[k]["min"]["character_id"],
                        count=tiers[k]["min"]["count"],
                    ),
                    max=TierListUnit(
                        character_id=tiers[k]["max"]["character_id"],
                        count=tiers[k]["max"]["count"],
                    ),
                )

        data = TierListUnitResponse(data=TierListUnitRanks(**tiers))
    except DoesNotExist:
        response.status_code = 200
        return TierListCompositionResponse(
            error=ErrorResponse(
                status_code=200, message="No games found in stat system"
            )
        )

    return data


@router.get("/player/{puuid}/placement", response_model=PlayerPlacementResponse)
@scope_required([Scope.read, Scope.write])
async def get_player_placement(
    request: Request,
    response: Response,
    puuid: str,
    region: RiotHost,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        player = (
            await TFTPlayer.get(puuid=puuid, region=region)
            .prefetch_related("participant")
            .filter(
                **generate_kwargs_structure(
                    event, tournament, stage, prefix="participant__game__"
                )
            )
            .annotate(
                min_placement=TMax("participant__placement"),
                avg_placement=TAvg("participant__placement"),
                max_placement=TMin("participant__placement"),
            )
        )

        data = PlayerPlacementResponse(
            data=PlayerPlacement(
                min=player.min_placement,
                avg=player.avg_placement,
                max=player.max_placement,
            )
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail=f"Player {puuid} from region {region.value} not found in stat system",
        )

    return data


@router.get("/player/{puuid}/kill", response_model=PlayerKillResponse)
@scope_required([Scope.read, Scope.write])
async def get_player_kill(
    request: Request,
    response: Response,
    puuid: str,
    region: RiotHost,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        player = (
            await TFTPlayer.get(puuid=puuid, region=region)
            .prefetch_related("participant")
            .filter(
                **generate_kwargs_structure(
                    event, tournament, stage, prefix="participant__game__"
                )
            )
            .annotate(
                min_players_eliminated=TMin("participant__players_eliminated"),
                avg_players_eliminated=TAvg("participant__players_eliminated"),
                max_players_eliminated=TMax("participant__players_eliminated"),
                sum_players_eliminated=TSum("participant__players_eliminated"),
            )
        )

        data = PlayerKillResponse(
            data=PlayerKill(
                min=player.min_players_eliminated,
                avg=player.avg_players_eliminated,
                max=player.max_players_eliminated,
                sum=player.sum_players_eliminated,
            )
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail=f"Player {puuid} from region {region.value} not found in stat system",
        )

    return data


@router.get("/player/{puuid}/death-round", response_model=DeathRoundResponse)
@scope_required([Scope.read, Scope.write])
async def get_player_death_round(
    request: Request,
    response: Response,
    puuid: str,
    region: RiotHost,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        player = (
            await TFTPlayer.get(puuid=puuid, region=region)
            .prefetch_related("participant")
            .filter(
                **generate_kwargs_structure(
                    event, tournament, stage, prefix="participant__game__"
                )
            )
            .annotate(
                min_last_round=TMin("participant__last_round"),
                avg_last_round=TAvg("participant__last_round"),
                max_last_round=TMax("participant__last_round"),
            )
        )

        data = DeathRoundResponse(
            data=DeathRound(
                min=player.min_last_round,
                avg=player.avg_last_round,
                max=player.max_last_round,
            )
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail=f"Player {puuid} from region {region.value} not found in stat system",
        )

    return data


@router.get("/games/damage", response_model=GamesDamageResponse)
@scope_required([Scope.read, Scope.write])
async def get_games_damage(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        players = (
            await TFTPlayer.all()
            .prefetch_related("participant")
            .filter(
                **generate_kwargs_structure(
                    event, tournament, stage, prefix="participant__game__"
                )
            )
            .exclude(participant=None)
            .annotate(
                min_total_damage_to_players=TMin(
                    "participant__total_damage_to_players"
                ),
                max_total_damage_to_players=TMax(
                    "participant__total_damage_to_players"
                ),
                sum_total_damage_to_players=TSum(
                    "participant__total_damage_to_players"
                ),
                count_game_played=TCount("participant"),
            )
        )

        if len(players) == 0:
            raise DoesNotExist

        total = 0
        nb_players = 0
        min = {
            "puuid": players[0].puuid,
            "damage": players[0].min_total_damage_to_players,
        }
        max = {
            "puuid": players[0].puuid,
            "damage": players[0].max_total_damage_to_players,
        }

        for player in players:
            total += player.sum_total_damage_to_players
            nb_players += player.count_game_played

            if min["damage"] > player.min_total_damage_to_players:
                min["puuid"] = player.puuid
                min["damage"] = player.min_total_damage_to_players

            if max["damage"] < player.max_total_damage_to_players:
                max["puuid"] = player.puuid
                max["damage"] = player.max_total_damage_to_players

        data = GamesDamageResponse(
            data=GamesDamageRanks(
                min=GamesDamage(
                    puuid=min["puuid"],
                    damage=min["damage"],
                ),
                avg=total / nb_players,
                max=GamesDamage(
                    puuid=max["puuid"],
                    damage=max["damage"],
                ),
                sum=total,
            )
        )
    except DoesNotExist:
        response.status_code = 200
        return TierListCompositionResponse(
            error=ErrorResponse(
                status_code=200, message="No games found in stat system"
            )
        )

    return data


@router.get("/games/time", response_model=GamesTimeResponse)
@scope_required([Scope.read, Scope.write])
async def get_games_time(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        game = (
            await TFTGame.all()
            .filter(**generate_kwargs_structure(event, tournament, stage))
            .annotate(
                min_game_length=TMin("game_length"),
                avg_game_length=TAvg("game_length"),
                max_game_length=TMax("game_length"),
                sum_game_length=TSum("game_length"),
            )
            .first()
        )

        if game.game_length is None:
            raise DoesNotExist

        time_elapsed = {}
        for stat, game_time_elapsed in [
            ("min_time", game.min_game_length),
            ("avg_time", game.avg_game_length),
            ("max_time", game.max_game_length),
            ("sum_time", game.sum_game_length),
        ]:
            mm, ss = divmod(game_time_elapsed, 60)
            hh, mm = divmod(mm, 60)
            dd, hh = divmod(hh, 24)
            time_elapsed[stat] = TimeElapsed(second=ss, minute=mm, hour=hh, day=dd)

        data = GamesTimeResponse(
            data=GamesTime(
                min_time=time_elapsed["min_time"],
                avg_time=time_elapsed["avg_time"],
                max_time=time_elapsed["max_time"],
                sum_time=time_elapsed["sum_time"],
            )
        )
    except DoesNotExist:
        response.status_code = 200
        return TierListCompositionResponse(
            error=ErrorResponse(
                status_code=200, message="No games found in stat system"
            )
        )

    return data


@router.get(
    "/game/{match_id}/damage",
    response_model=GameDamageResponse,
)
@scope_required([Scope.read, Scope.write])
async def get_game_damage(request: Request, response: Response, match_id: str):
    try:
        game = await TFTGame.get(match_id=match_id).prefetch_related("participant")
        participants = await game.participant.order_by(
            "-total_damage_to_players"
        ).prefetch_related("player")

        damages = []
        for i in range(0, len(participants)):
            damages.append(
                GameDamage(
                    puuid=participants[i].player.puuid,
                    damage=participants[i].total_damage_to_players,
                )
            )
        data = GameDamageResponse(data=damages)

    except DoesNotExist:
        raise HTTPException(
            status_code=404, detail=f"Game {match_id} not found in stat system"
        )

    return data
