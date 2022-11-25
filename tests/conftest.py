from typing import Generator

import pytest
from asyncclick.testing import CliRunner
from tortoise import current_transaction_map
from tortoise.contrib.test import finalizer, initializer

from les_stats.main import create_app
from tests.utils import CustomClient

app = create_app()


@pytest.fixture()
def client() -> Generator:
    initializer(["les_stats.models"])
    current_transaction_map["default"] = current_transaction_map["models"]
    with CustomClient(app) as c:
        yield c
    finalizer()


@pytest.fixture()
def runner() -> Generator:
    initializer(["les_stats.models"])
    yield CliRunner()
    finalizer()


@pytest.fixture
def non_mocked_hosts() -> list:
    return ["testserver"]
