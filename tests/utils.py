import json
import os
import re
from typing import Any, Dict, List

from fastapi.testclient import TestClient

from les_stats.models.internal.auth import Api, Scope
from les_stats.utils.auth import API_KEY_SIZE_MAX, get_digest


class CustomClient(TestClient):
    async def test_api_scope(
        self, method: str, url: str, allowed_scopes: List[Scope], json: dict = None
    ):
        allowed_scopes_values = [
            allowed_scope.value for allowed_scope in allowed_scopes
        ]
        for allowed_scope in allowed_scopes_values:
            api_key = ("a" * API_KEY_SIZE_MAX)[: -len(allowed_scope)] + allowed_scope
            await Api.get_or_create(
                name=f"TEST_SCOPE_{allowed_scope}",
                scope=allowed_scope,
                api_key=get_digest(api_key),
            )
            r = self.request(method, url, headers={"x-api-key": api_key}, json=json)
            assert r.status_code != 403

        for not_allowed_scope in list(
            set(list(Scope.__members__.keys())) - set(allowed_scopes_values)
        ):
            api_key = ("a" * API_KEY_SIZE_MAX)[
                : -len(not_allowed_scope)
            ] + not_allowed_scope
            await Api.get_or_create(
                name=f"TEST_SCOPE_{not_allowed_scope}",
                scope=not_allowed_scope,
                api_key=get_digest(api_key),
            )
            r = self.request(method, url, headers={"x-api-key": api_key}, json=json)
            assert r.status_code == 403

        r = self.request(method, url, json=json)
        assert r.status_code == 422

    async def test_api(self, method: str, url: str, scope: str, json: dict = None):
        scope = scope.value
        api_key = ("a" * API_KEY_SIZE_MAX)[: -len(scope)] + scope
        await Api.get_or_create(
            name=f"TEST_SCOPE_{scope}", scope=scope, api_key=get_digest(api_key)
        )
        print(url)
        return self.request(method, url, headers={"x-api-key": api_key}, json=json)


def get_json_response(filename: str) -> Dict[Any, Any]:
    filename = re.sub("{.*}", "", filename)
    with open(os.path.join("tests/mocked_data/", filename), "r") as f:
        return json.loads(f.read())
