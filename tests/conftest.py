import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer
from tortoise.transactions import current_transaction_map

from les_stats.main import create_app

app = create_app()


@pytest.fixture()
def client() -> Generator:
    initializer(["les_stats.models"])
    current_transaction_map["default"] = current_transaction_map["models"]
    with TestClient(app) as c:
        yield c
    finalizer()


@pytest.fixture(scope="module")
def event_loop() -> Generator:
    yield asyncio.get_event_loop()
