from enum import Enum
from typing import List

import httpx
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from les_stats.client_api.client import ClientAPI
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
from les_stats.schemas.client_api.data import DataResponse, ErrorResponse
from les_stats.utils.config import get_settings
from les_stats.utils.metrics import (
    metric_game,
    metric_request_failed_processing_seconds_api,
    metric_request_rate_limit_total_api,
    metric_request_success_processing_seconds_api,
)


class RiotHost(str, Enum):
    americas = "americas"
    asia = "asia"
    europe = "europe"
    sea = "sea"


class RiotGame(str, Enum):
    valorant = "valorant"
    lol = "lol"
    tft = "tft"


class RiotAPI(ClientAPI):
    def __init__(self, game: RiotGame) -> None:
        self.game = game
        self.routing = game
        self.api_key = game
        self.base_api_url = "api.riotgames.com"
        super().__init__(httpx.AsyncClient(headers={"X-Riot-Token": self.api_key}))

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

    def get_region(self, text):
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

    def handle_response(self, resps: List[httpx.Response]) -> List[DataResponse]:
        data = []
        for resp in resps:
            req_time_sec = resp.elapsed.total_seconds()
            if resp.is_success:
                data.append(DataResponse(data=resp.json()))
                metric_request_success_processing_seconds_api.labels(self.game).observe(
                    req_time_sec
                )
            else:
                data.append(
                    DataResponse(
                        error=ErrorResponse(
                            status_code=resp.status_code, message=resp.json()
                        )
                    )
                )
                if resp.status_code == 429:
                    metric_request_rate_limit_total_api.labels(self.game).inc()
                metric_request_failed_processing_seconds_api.labels(self.game).observe(
                    req_time_sec
                )

        return data

    async def save_valorant_games(self, matches_id: List[str]) -> List[DataResponse]:
        raise NotImplementedError

    async def delete_valorant_games(self, matches_id: List[str]) -> List[DataResponse]:
        raise NotImplementedError

    async def save_lol_games(self, matches_id: List[str]) -> List[DataResponse]:
        raise NotImplementedError

    async def delete_lol_games(self, matches_id: List[str]) -> List[DataResponse]:
        raise NotImplementedError

    async def save_tft_games(self, matches_id: List[str]) -> List[DataResponse]:
        data = []

        for match_id in matches_id:
            try:
                await TFTGame.get(match_id=match_id)
                data.append(
                    DataResponse(
                        error=ErrorResponse(
                            status_code=409, message=f"Game {match_id} already saved"
                        )
                    )
                )
                continue
            except DoesNotExist:
                pass

            req = (await self.get_matches([match_id]))[0]
            data.append(req)
            if req.data:
                g = req.data
            else:
                continue

            async with in_transaction("default") as connection:
                metadata = g["metadata"]
                info = g["info"]
                game = await TFTGame(
                    match_id=metadata["match_id"],
                    data_version=metadata["data_version"],
                    game_datetime=info["game_datetime"],
                    game_length=info["game_length"],
                    game_version=info["game_version"],
                    queue_id=info["queue_id"],
                    tft_set_number=info["tft_set_number"],
                    tft_game_type=info["tft_game_type"],
                )
                if "tft_set_core_name" in info:
                    game.tft_set_core_name = info["tft_set_core_name"]
                await game.save(using_db=connection)

                for p in info["participants"]:
                    player, _ = await TFTPlayer.get_or_create(
                        puuid=p["puuid"], using_db=connection
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

        metric_game.labels(self.game).inc()
        return data

    async def delete_tft_games(self, matches_id: List[str]) -> List[DataResponse]:
        data = []

        for match_id in matches_id:
            deleted_count = await TFTGame.filter(match_id=match_id).delete()
            if not deleted_count:
                data.append(
                    DataResponse(
                        error=ErrorResponse(
                            status_code=404, message=f"Game {match_id} not found"
                        )
                    )
                )
                metric_game.labels(self.game).dec()
            else:
                data.append(DataResponse(data=f"Game {match_id} deleted"))

        return data

    async def get_summoners_name(
        self, encrypted_puuids: List[str]
    ) -> List[DataResponse]:
        reqs = []
        for encrypted_puuid in encrypted_puuids:
            reqs.append(
                self.session.build_request(
                    "GET",
                    self.build_url(
                        self.routing,
                        f"/{self.game}/summoner/v1/summoners/by-puuid/{encrypted_puuid}",
                    ),
                )
            )

        return self.handle_response(await self.make_request(reqs))

    async def get_summoners_puuid(
        self, summoners_name: List[str]
    ) -> List[DataResponse]:
        reqs = []
        for summoner_name in summoners_name:
            reqs.append(
                self.session.build_request(
                    "GET",
                    self.build_url(
                        self.routing,
                        f"/{self.game}/summoner/v1/summoners/by-name/{summoner_name}",
                    ),
                )
            )

        return self.handle_response(await self.make_request(reqs))

    async def get_match_list(
        self,
        puuid: str,
        host: RiotHost,
        start: int = 0,
        end_time: int = None,
        start_time: int = None,
        count: int = 20,
    ) -> DataResponse:
        match_list_url = ""
        if self.game == RiotGame.valorant:
            match_list_url = f"/{self.game}/match/v1/matchlists/by-puuid/{puuid}"
        elif self.game == RiotGame.lol:
            match_list_url = f"/{self.game}/match/v5/matches/by-puuid/{puuid}/ids"
        elif self.game == RiotGame.tft:
            match_list_url = f"/{self.game}/match/v1/matches/by-puuid/{puuid}/ids"

        params = {
            "start": start,
            "count": count,
        }
        if end_time:
            params["endTime"] = end_time
        if start_time:
            params["startTime"] = start_time

        return self.handle_response(
            (
                await self.make_request(
                    [
                        self.session.build_request(
                            "GET",
                            self.build_url(host, match_list_url),
                            params=params,
                        )
                    ]
                )
            )[0]
        )

    async def get_matches(self, matches_id: List[str]) -> List[DataResponse]:
        if self.game == RiotGame.valorant:
            match_url = f"/{self.game}/match/v1/matches"
        elif self.game == RiotGame.lol:
            match_url = f"/{self.game}/match/v5/matches"
        else:
            match_url = f"/{self.game}/match/v1/matches"

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
