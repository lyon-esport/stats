import datetime
from typing import List, Tuple, Union

import httpx
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from les_stats.client_api.client import ClientAPI
from les_stats.metrics.internal.metrics import metric_game
from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from les_stats.models.lol.game import LolGame
from les_stats.models.tft.game import (
    TFTAugment,
    TFTCompanion,
    TFTCurrentTrait,
    TFTCurrentUnit,
    TFTGame,
    TFTItem,
    TFTParticipant,
    TFTPlayer,
    TFTTrait,
    TFTUnit,
)
from les_stats.models.valorant.game import ValorantGame
from les_stats.schemas.client_api.data import DataResponse, ErrorResponse
from les_stats.schemas.riot.game import GameSaveIn_Pydantic, RiotGame, RiotHost
from les_stats.utils.config import get_settings


class RiotAPI(ClientAPI):
    def __init__(self, game: RiotGame) -> None:
        self.routing = game
        self.api_key = game
        self.base_api_url = "api.riotgames.com"
        super().__init__(
            httpx.AsyncClient(headers={"X-Riot-Token": self.api_key}), game
        )

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, game: str):
        api_key = ""

        if game == RiotGame.valorant:
            api_key = get_settings().VALORANT_API_KEY
        elif game == RiotGame.lol:
            api_key = get_settings().LOL_API_KEY
        elif game == RiotGame.tft:
            api_key = get_settings().TFT_API_KEY

        self._api_key = api_key

    @property
    def routing(self):
        return self._routing

    @routing.setter
    def routing(self, game: str):
        routing = ""

        if game == RiotGame.valorant:
            routing = get_settings().VALORANT_API_ROUTING
        elif game == RiotGame.lol:
            routing = get_settings().LOL_API_ROUTING
        elif game == RiotGame.tft:
            routing = get_settings().TFT_API_ROUTING

        self._routing = routing

    def build_url(self, host: str, endpoint: str) -> str:
        return f"https://{host}.{self.base_api_url}{endpoint}"

    @classmethod
    def get_region(cls, text):
        if any(
            routing.upper() in text.upper() for routing in ["BR", "LAN", "LAS", "NA"]
        ):
            host = RiotHost.americas
        elif any(routing.upper() in text.upper() for routing in ["JP", "KR"]):
            host = RiotHost.asia
        elif any(
            routing.upper() in text.upper() for routing in ["EUNE", "EUW", "RU", "TR"]
        ):
            host = RiotHost.europe
        else:
            host = RiotHost.sea

        return host

    async def save_valorant_games(
        self, matches: List[GameSaveIn_Pydantic]
    ) -> List[DataResponse]:
        raise NotImplementedError

    async def update_valorant_games(
        self, matches: List[GameSaveIn_Pydantic]
    ) -> List[DataResponse]:
        return await self._update_games(matches, ValorantGame)

    async def delete_valorant_games(self, matches_id: List[str]) -> List[DataResponse]:
        return await self._delete_games(matches_id, ValorantGame)

    async def save_lol_games(
        self, matches: List[GameSaveIn_Pydantic]
    ) -> List[DataResponse]:
        raise NotImplementedError

    async def update_lol_games(
        self, matches: List[GameSaveIn_Pydantic]
    ) -> List[DataResponse]:
        return await self._update_games(matches, LolGame)

    async def delete_lol_games(self, matches_id: List[str]) -> List[DataResponse]:
        return await self._delete_games(matches_id, LolGame)

    async def save_tft_games(
        self,
        matches: List[GameSaveIn_Pydantic],
        min_player: int = 0,
        players: List[str] = [],
    ) -> List[DataResponse]:
        http_code = None
        data = []

        for match in matches:
            try:
                await TFTGame.get(match_id=match.id)
                if http_code is None:
                    http_code = 409
                elif http_code != 409:
                    http_code = 207
                data.append(
                    DataResponse(
                        error=ErrorResponse(
                            status_code=409, message=f"Game {match.id} already saved"
                        )
                    )
                )
                continue
            except DoesNotExist:
                pass

            game_tags = {}
            try:
                for instance, value in [
                    (Event, match.event),
                    (Tournament, match.tournament),
                    (Stage, match.stage),
                ]:
                    http_code, result = await self._get_game_tags(
                        http_code, instance, value
                    )
                    if isinstance(result, instance):
                        game_tags[type(result).__name__.lower()] = result
                    elif isinstance(result, DataResponse):
                        data.append(result)
                        raise DoesNotExist
            except DoesNotExist:
                continue

            req_http_code, req = await self.get_matches([match.id])
            req = req[0]
            if req.data:
                g = req.data
            else:
                if http_code is None:
                    http_code = req_http_code
                elif http_code != req_http_code:
                    http_code = 207
                data.append(req)
                continue

            if len(players) > 0:
                nb_players_matched = sum(
                    participant in players
                    for participant in g["metadata"]["participants"]
                )
                if min_player > nb_players_matched:
                    if http_code is None:
                        http_code = 200
                    elif http_code != req_http_code:
                        http_code = 207
                    data.append(
                        DataResponse(
                            error=ErrorResponse(
                                status_code=200,
                                message=f"{nb_players_matched} players matched, needed {min_player}",
                            )
                        )
                    )
                    continue

            async with in_transaction("default") as connection:
                metadata = g["metadata"]
                info = g["info"]
                game = await TFTGame(
                    match_id=metadata["match_id"],
                    data_version=metadata["data_version"],
                    game_datetime=datetime.datetime.utcfromtimestamp(
                        int(str(info["game_datetime"])[:-3])
                    ),
                    game_length=info["game_length"],
                    game_version=info["game_version"],
                    queue_id=info["queue_id"],
                    tft_set_number=info["tft_set_number"],
                    tft_game_type=info["tft_game_type"],
                )
                if "tft_set_core_name" in info:
                    game.tft_set_core_name = info["tft_set_core_name"]
                if match.event:
                    game.event = game_tags["event"]
                if match.tournament:
                    game.tournament = game_tags["tournament"]
                if match.stage:
                    game.stage = game_tags["stage"]
                await game.save(using_db=connection)

                for p in info["participants"]:
                    player, _ = await TFTPlayer.get_or_create(
                        puuid=p["puuid"],
                        region=self.get_region(metadata["match_id"]),
                        using_db=connection,
                    )
                    companion, _ = await TFTCompanion.get_or_create(
                        content_id=p["companion"]["content_ID"],
                        skin_id=p["companion"]["skin_ID"],
                        species=p["companion"]["species"],
                        using_db=connection,
                    )
                    participant = await TFTParticipant(
                        gold_left=p["gold_left"],
                        last_round=p["last_round"],
                        level=p["level"],
                        placement=p["placement"],
                        players_eliminated=p["players_eliminated"],
                        time_eliminated=p["time_eliminated"],
                        total_damage_to_players=p["total_damage_to_players"],
                        companion=companion,
                        player=player,
                        game=game,
                    )
                    await participant.save(using_db=connection)

                    for a in p["augments"]:
                        augment, _ = await TFTAugment.get_or_create(
                            name=a, using_db=connection
                        )
                        await participant.augments.add(augment)

                    for t in p["traits"]:
                        trait, _ = await TFTTrait.get_or_create(
                            name=t["name"], using_db=connection
                        )
                        current_trait = await TFTCurrentTrait(
                            num_units=t["num_units"],
                            style=t["style"],
                            tier_current=t["tier_current"],
                            tier_total=t["tier_total"],
                            trait=trait,
                            participant=participant,
                        )
                        await current_trait.save(using_db=connection)

                    for u in p["units"]:
                        unit, _ = await TFTUnit.get_or_create(
                            character_id=u["character_id"], using_db=connection
                        )
                        current_unit = await TFTCurrentUnit(
                            name=u["name"],
                            rarity=u["rarity"],
                            tier=u["tier"],
                            unit=unit,
                            participant=participant,
                        )
                        if "chosen" in u:
                            current_unit.chosen = u["chosen"]
                        await current_unit.save(using_db=connection)

                        for i in range(0, len(u["items"])):
                            item, _ = await TFTItem.get_or_create(
                                id=u["items"][i], using_db=connection
                            )
                            if "itemNames" in u:
                                item.name = u["itemNames"][i]
                                await item.save(using_db=connection)
                            await current_unit.items.add(item)

            if http_code is None:
                http_code = 200
            elif http_code != 200:
                http_code = 207
            data.append(DataResponse(data=f"Game {match.id} saved"))

            metric_game.labels(
                match.event, match.tournament, match.stage, self.game.value
            ).inc()

        return http_code, data

    async def update_tft_games(
        self, matches: List[GameSaveIn_Pydantic]
    ) -> List[DataResponse]:
        return await self._update_games(matches, TFTGame)

    async def delete_tft_games(self, matches_id: List[str]) -> List[DataResponse]:
        return await self._delete_games(matches_id, TFTGame)

    async def _update_games(
        self,
        matches: List[GameSaveIn_Pydantic],
        game_type: Union[TFTGame, ValorantGame],
    ) -> List[DataResponse]:
        http_code = None
        data = []
        for match in matches:
            try:
                game = await game_type.get(match_id=match.id)
            except DoesNotExist:
                if http_code is None:
                    http_code = 404
                elif http_code != 404:
                    http_code = 207
                data.append(
                    DataResponse(
                        error=ErrorResponse(
                            status_code=404, message=f"Game {match.id} not found"
                        )
                    )
                )
                continue

            game_tags = {}
            try:
                for instance, value in [
                    (Event, match.event),
                    (Tournament, match.tournament),
                    (Stage, match.stage),
                ]:
                    http_code, result = await self._get_game_tags(
                        http_code, instance, value
                    )
                    if isinstance(result, instance):
                        game_tags[type(result).__name__.lower()] = result
                    elif isinstance(result, DataResponse):
                        data.append(result)
                        raise DoesNotExist
            except DoesNotExist:
                continue

            old_event = game.event if hasattr(game, "event") else None
            old_tournament = game.tournament if hasattr(game, "tournament") else None
            old_stage = game.stage if hasattr(game, "stage") else None
            if match.event:
                game.event = game_tags["event"]
            else:
                game.event = None
            if match.tournament:
                game.tournament = game_tags["tournament"]
            else:
                game.tournament = None
            if match.stage:
                game.stage = game_tags["stage"]
            else:
                game.stage = None
            await game.save()
            if http_code is None:
                http_code = 200
            elif http_code != 200:
                http_code = 207
            data.append(DataResponse(data=f"Game {match.id} updated"))
            metric_game.labels(
                self.game.value, old_event, old_tournament, old_stage
            ).dec()
            metric_game.labels(
                self.game.value, match.event, match.tournament, match.stage
            ).inc()

        return http_code, data

    async def _delete_games(
        self, matches_id: List[str], game_type: Union[TFTGame, ValorantGame]
    ) -> List[DataResponse]:
        http_code = None
        data = []

        for match_id in matches_id:
            try:
                game = await game_type.get(match_id=match_id)
            except DoesNotExist:
                if http_code is None:
                    http_code = 404
                elif http_code != 404:
                    http_code = 207
                data.append(
                    DataResponse(
                        error=ErrorResponse(
                            status_code=404, message=f"Game {match_id} not found"
                        )
                    )
                )
                continue
            old_event = game.event if hasattr(game, "event") else None
            old_tournament = game.tournament if hasattr(game, "tournament") else None
            old_stage = game.stage if hasattr(game, "stage") else None
            await game.delete()
            if http_code is None:
                http_code = 200
            elif http_code != 200:
                http_code = 207
            data.append(DataResponse(data=f"Game {match_id} deleted"))
            metric_game.labels(
                self.game.value, old_event, old_tournament, old_stage
            ).dec()

        return http_code, data

    async def get_summoners_name(
        self, encrypted_puuids: List[str]
    ) -> Tuple[int, List[DataResponse]]:
        reqs = []
        for encrypted_puuid in encrypted_puuids:
            match_list_url = ""
            if self.game == RiotGame.valorant:
                match_list_url = f"/{self.game.value}/summoner/v1/summoners/by-puuid/{encrypted_puuid}"
            elif self.game == RiotGame.lol:
                match_list_url = f"/{self.game.value}/summoner/v4/summoners/by-puuid/{encrypted_puuid}"
            elif self.game == RiotGame.tft:
                match_list_url = f"/{self.game.value}/summoner/v1/summoners/by-puuid/{encrypted_puuid}"

            reqs.append(
                self.session.build_request(
                    "GET",
                    self.build_url(
                        self.routing,
                        match_list_url,
                    ),
                )
            )

        return self.handle_response(await self.make_request(reqs))

    async def get_summoners_puuid(
        self, summoners_name: List[str]
    ) -> Tuple[int, List[DataResponse]]:
        reqs = []
        for summoner_name in summoners_name:
            match_list_url = ""
            if self.game == RiotGame.valorant:
                match_list_url = (
                    f"/{self.game.value}/summoner/v1/summoners/by-name/{summoner_name}"
                )
            elif self.game == RiotGame.lol:
                match_list_url = (
                    f"/{self.game.value}/summoner/v4/summoners/by-name/{summoner_name}"
                )
            elif self.game == RiotGame.tft:
                match_list_url = (
                    f"/{self.game.value}/summoner/v1/summoners/by-name/{summoner_name}"
                )

            reqs.append(
                self.session.build_request(
                    "GET",
                    self.build_url(
                        self.routing,
                        match_list_url,
                    ),
                )
            )

        return self.handle_response(await self.make_request(reqs))

    async def get_matches_list(
        self,
        puuids: List[str],
        start: int = 0,
        end_time: int = None,
        start_time: int = None,
        count: int = 20,
    ) -> DataResponse:
        reqs = []

        for puuid in puuids:
            match_list_url = ""
            if self.game == RiotGame.valorant:
                match_list_url = (
                    f"/{self.game.value}/match/v1/matchlists/by-puuid/{puuid}"
                )
            elif self.game == RiotGame.lol:
                match_list_url = (
                    f"/{self.game.value}/match/v5/matches/by-puuid/{puuid}/ids"
                )
            elif self.game == RiotGame.tft:
                match_list_url = (
                    f"/{self.game.value}/match/v1/matches/by-puuid/{puuid}/ids"
                )

            params = {
                "start": start,
                "count": count,
            }
            if end_time:
                params["endTime"] = end_time
            if start_time:
                params["startTime"] = start_time

            reqs.append(
                self.session.build_request(
                    "GET",
                    self.build_url(self.routing, match_list_url),
                    params=params,
                )
            )

        return self.handle_response(await self.make_request(reqs))

    async def get_matches(
        self, matches_id: List[str]
    ) -> Tuple[int, List[DataResponse]]:
        if self.game == RiotGame.valorant:
            match_url = f"/{self.game.value}/match/v1/matches"
        elif self.game == RiotGame.lol:
            match_url = f"/{self.game.value}/match/v5/matches"
        else:
            match_url = f"/{self.game.value}/match/v1/matches"

        reqs = []
        for match_id in matches_id:
            reqs.append(
                self.session.build_request(
                    "GET",
                    self.build_url(
                        self.get_region(match_id), f"{match_url}/{match_id}"
                    ),
                )
            )

        return self.handle_response(await self.make_request(reqs))

    async def get_summoners_rank(
        self, summoners_id: List[str]
    ) -> Tuple[int, List[DataResponse]]:
        if self.game == RiotGame.valorant:
            raise NotImplementedError
        elif self.game == RiotGame.lol:
            match_url = f"/{self.game.value}/league/v4/entries/by-summoner"
        else:
            match_url = f"/{self.game.value}/league/v1/entries/by-summoner"

        reqs = []
        for summoner_id in summoners_id:
            reqs.append(
                self.session.build_request(
                    "GET",
                    self.build_url(self.routing, f"{match_url}/{summoner_id}"),
                )
            )

        return self.handle_response(await self.make_request(reqs))
