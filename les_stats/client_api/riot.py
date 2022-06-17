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


class RiotAPI:
    def __init__(self, api_key: str, routing: str) -> None:
        self.api_key = api_key
        self.routing = routing
        self.base_api_url = "api.riotgames.com"

    def build_url(self, endpoint: str) -> str:
        return f"https://{self.routing}.{self.base_api_url}{endpoint}"

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

        return responses

    async def test(self):
        return await self.make_request(
            [Req(method="GET", endpoint="/lol/status/v4/platform-data")]
        )
