import asyncio
from typing import List, Union

import httpx

from les_stats.schemas.client_api.data import DataResponse


class ClientAPI:
    def __init__(self, httpx_client: httpx.AsyncClient):
        self.session = httpx_client

    def build_url(self, *args, **kwargs) -> str:
        raise NotImplementedError

    async def make_request(self, reqs: List[httpx.Request]) -> List[httpx.Response]:
        tasks = []
        responses = []

        for req in reqs:
            tasks.append(asyncio.ensure_future(self.session.send(req)))

            responses = await asyncio.gather(*tasks)

        return responses

    def handle_response(
        self, resps: List[httpx.Response]
    ) -> Union[DataResponse, List[DataResponse]]:
        raise NotImplementedError
