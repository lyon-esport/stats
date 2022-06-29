from enum import Enum
from typing import List

import httpx

from les_stats.client_api.client import ClientAPI, Req
from les_stats.utils.config import get_settings
from les_stats.utils.metrics import (
    metric_request_failed_processing_seconds_api,
    metric_request_rate_limit_total_api,
    metric_request_success_processing_seconds_api,
)


class RiotGame(str, Enum):
    valorant = "valorant"
    lol = "lol"


class RiotAPI(ClientAPI):
    def __init__(self, game: RiotGame) -> None:
        super().__init__(game, game.value)
        self.routing = game
        self.base_api_url = "api.riotgames.com"

    @ClientAPI.api_key.setter
    def api_key(self, game: str):
        api_key = ""

        if game == RiotGame.valorant:
            api_key = get_settings().VALORANT_API_KEY
        elif game == RiotGame.lol:
            api_key = get_settings().LOL_API_KEY

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

        self._routing = routing

    def build_url(self, endpoint: str) -> str:
        return f"https://{self.routing}.{self.base_api_url}{endpoint}"

    def _generate_response_metrics(self, resps: List[httpx.Response]) -> None:
        for resp in resps:
            req_time_sec = resp.elapsed.total_seconds()

            if resp.is_success:
                metric_request_success_processing_seconds_api.labels(self.game).observe(
                    req_time_sec
                )
            else:
                if resp.status_code == 429:
                    metric_request_rate_limit_total_api.labels(self.game).inc()
                metric_request_failed_processing_seconds_api.labels(self.game).observe(
                    req_time_sec
                )

    async def test(self):
        return await self.make_request(
            [Req(method="GET", endpoint="/lol/status/v4/platform-data")]
        )
