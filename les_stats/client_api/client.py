import asyncio
from typing import List, Tuple, Union

import httpx
from tortoise.exceptions import DoesNotExist

from les_stats.metrics.metrics import (
    metric_request_failed_processing_seconds_api,
    metric_request_http_code_total_api,
    metric_request_success_processing_seconds_api,
)
from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament
from les_stats.schemas.client_api.data import DataResponse, ErrorResponse


class ClientAPI:
    def __init__(self, httpx_client: httpx.AsyncClient, game: str):
        self.session = httpx_client
        self.game = game

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
    ) -> Tuple[int, List[DataResponse]]:
        http_code = None
        data = []
        for resp in resps:
            if http_code is None:
                http_code = resp.status_code
            elif http_code != 207 and http_code != resp.status_code:
                http_code = 207
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
                metric_request_http_code_total_api.labels(
                    resp.status_code, self.game
                ).inc()
                metric_request_failed_processing_seconds_api.labels(self.game).observe(
                    req_time_sec
                )

        return http_code, data

    async def _get_game_tags(
        self, http_code: int, instance: Union[Event, Tournament, Stage], value: str
    ) -> Tuple[int, Union[Event, Tournament, Stage]]:
        """
        :param http_code: Current http_code
        :param instance:
        :param value:
        :return: http_code = 200 or 404 (object exist or not) and result = object or DataResponse (object exist or not)
        """
        response = None
        if value:
            try:
                response = await instance.get(name=value)
            except DoesNotExist:
                response = DataResponse(
                    error=ErrorResponse(
                        status_code=404,
                        message=f"{instance.__name__} {value} does not exist",
                    )
                )
            if not isinstance(response, instance):
                if http_code is None:
                    http_code = 404
                elif http_code != 404:
                    http_code = 207

        return http_code, response
