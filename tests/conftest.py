from typing import Generator

import pytest
from asgi_lifespan import LifespanManager
from asyncclick.testing import CliRunner
from tortoise.contrib.test import finalizer, initializer

from les_stats.main import create_app
from les_stats.utils.db import init_db
from tests.utils import CustomClient

app = create_app()


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client() -> Generator:
    await init_db()
    async with LifespanManager(app):
        async with CustomClient(app=app, base_url="http://testserver") as c:
            yield c


@pytest.fixture()
def runner() -> Generator:
    initializer(["les_stats.models"])
    yield CliRunner()
    finalizer()


@pytest.fixture
def non_mocked_hosts() -> list:
    return ["testserver"]
