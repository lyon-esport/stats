import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Request, Response
from tortoise.exceptions import DoesNotExist
from tortoise.functions import Avg, Max, Min

from les_stats.client_api.riot import RiotAPI
from les_stats.models.internal.auth import Scope
from les_stats.models.tft.game import TFTGame, TFTPlayer
from les_stats.schemas.client_api.data import DataResponse, ErrorResponse
from les_stats.schemas.internal.generic import GameTimeElapsed
from les_stats.schemas.riot.game import RiotGame
from les_stats.schemas.tft.stat import (
    DeathRoundResponse,
    GameTime,
    GameTimeResponse,
    RankingDamage,
    RankingDamageResponse,
)
from les_stats.utils.auth import scope_required

router = APIRouter()


@router.get("/tier-list/composition", response_model=List[DataResponse])
@scope_required([Scope.read])
async def get_tier_list_composition(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/tier-list/items", response_model=DataResponse)
@scope_required([Scope.read])
async def get_tier_list_item(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/tier-list/unit", response_model=DataResponse)
@scope_required([Scope.read])
async def get_tier_list_unit(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/player/rank", response_model=DataResponse)
@scope_required([Scope.read])
async def get_player_rank(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/player/position", response_model=DataResponse)
@scope_required([Scope.read])
async def get_player_position(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/player/kill", response_model=DataResponse)
@scope_required([Scope.read])
async def get_player_kill(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get(
    "/player/death_round", response_model=Union[List[DeathRoundResponse], ErrorResponse]
)
@scope_required([Scope.read])
async def get_games_death_round(
    request: Request,
    response: Response,
    puuid: str,
    region: str,
):
    data = []

    try:
        player = await TFTPlayer.get(puuid=puuid, region=region).prefetch_related(
            "participant"
        )
        participants = await player.participant.order_by(
            "-last_round"
        ).prefetch_related("game")
        print(participants)
    except DoesNotExist:
        response.status_code = 404
        data = ErrorResponse(
            status_code=404,
            message=f"Player {puuid} from region {region} not found in stat system",
        )

    return data


@router.get("/games/damage", response_model=DataResponse)
@scope_required([Scope.read])
async def get_games_damage(
    request: Request,
    response: Response,
):
    return DataResponse()


@router.get("/games/time", response_model=Union[GameTimeResponse, ErrorResponse])
@scope_required([Scope.read])
async def get_games_time(
    request: Request,
    response: Response,
    event: Optional[str] = None,
    tournament: Optional[str] = None,
    stage: Optional[str] = None,
):
    try:
        # check comment mettre les filtres en optionnel
        # check si annotate first suffit ou il faut all avant
        games = (
            await TFTGame.all()
            .annotate(
                min_game_length=Min("game_length"),
                avg_game_length=Avg("game_length"),
                max_game_length=Max("game_length"),
            )
            .first()
        )

        time_elapsed = {}
        for stat, game_time_elapsed in [
            ("min_time", games.min_game_length),
            ("avg_time", games.avg_game_length),
            ("max_time", games.max_game_length),
        ]:
            t = datetime.timedelta(seconds=game_time_elapsed)
            time_elapsed[stat] = GameTimeElapsed(
                second=t.second, minute=t.minute, hour=t.hour, day=t.day
            )

        data = GameTimeResponse(
            data=GameTime(
                min_time=time_elapsed["min_time"],
                avg_time=time_elapsed["avg_time"],
                max_time=time_elapsed["max_time"],
            )
        )
    except DoesNotExist:
        response.status_code = 404
        data = ErrorResponse(
            status_code=response.status_code, message="No game found in stat system"
        )

    return data


@router.get(
    "/game/ranking/damage",
    response_model=Union[List[RankingDamageResponse], ErrorResponse],
)
@scope_required([Scope.read])
async def get_game_ranking_damage(request: Request, response: Response, match_id: str):
    data = []

    try:
        game = await TFTGame.get(match_id=match_id).prefetch_related("participant")
        participants = await game.participant.order_by(
            "-total_damage_to_players"
        ).prefetch_related("player")
        response.status_code, players = await RiotAPI(RiotGame.tft).get_summoners_name(
            [participant.player.puuid for participant in participants]
        )
        for i, player in enumerate(players):
            if player.data:
                data.append(
                    RankingDamageResponse(
                        data=RankingDamage(
                            puuid=participants[i].player.puuid,
                            name=player.data["name"],
                            damage=participants[i].total_damage_to_players,
                        )
                    )
                )
            else:
                data.append(
                    RankingDamageResponse(
                        data=RankingDamage(
                            puuid=participants[i].puuid,
                            name="",
                            damage=participants[i].total_damage_to_players,
                        ),
                        error=player,
                    )
                )
    except DoesNotExist:
        response.status_code = 404
        data = ErrorResponse(
            status_code=404, message=f"Game {match_id} not found in stat system"
        )

    return data
