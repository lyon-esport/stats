import asyncio
from dataclasses import dataclass, field
from typing import Dict, List

import httpx


@dataclass
class Req:
    method: str
    endpoint: str
    body: Dict = field(default_factory=dict)
    params: str = field(default_factory=dict)


class ClientAPI:
    def __init__(self, api_key: str, game: str):
        self.api_key = api_key
        self.game = game

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = value

    def build_url(self, endpoint: str) -> str:
        raise NotImplementedError

    async def make_request(self, reqs: List[Req]) -> List[httpx.Response]:
        tasks = []

        async with httpx.AsyncClient() as client:
            for req in reqs:
                request = httpx.Request(req.method, self.build_url(req.endpoint))
                request.params = req.params
                request.body = req.body
                request.headers["X-Riot-Token"] = self.api_key
                tasks.append(asyncio.ensure_future(client.send(request)))

            responses = await asyncio.gather(*tasks)

        self._generate_response_metrics(responses)

        return responses

    def _generate_response_metrics(self, resps: List[httpx.Response]) -> None:
        raise NotImplementedError
