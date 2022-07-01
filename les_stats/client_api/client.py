import asyncio
from dataclasses import dataclass
from typing import Any, List, Optional

import httpx


@dataclass
class Req:
    method: str
    endpoint: str
    params: Optional[httpx._types.HeaderTypes] = None
    json: Optional[Any] = None


class ClientAPI:
    def __init__(self, httpx_client: httpx.AsyncClient):
        self.session = httpx_client

    def build_url(self, endpoint: str) -> str:
        raise NotImplementedError

    async def make_request(self, reqs: List[Req]) -> List[httpx.Response]:
        tasks = []
        responses = []

        for req in reqs:
            request = self.session.build_request(
                req.method,
                self.build_url(req.endpoint),
                params=req.params,
                json=req.json,
            )
            tasks.append(asyncio.ensure_future(self.session.send(request)))

            responses = await asyncio.gather(*tasks)

        self._generate_response_metrics(responses)

        return responses

    def _generate_response_metrics(self, resps: List[httpx.Response]) -> None:
        raise NotImplementedError
