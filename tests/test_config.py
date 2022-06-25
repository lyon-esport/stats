from typing import List

import pytest
from pydantic import HttpUrl
from pydantic.error_wrappers import ValidationError

from les_stats.config import Settings


@pytest.mark.parametrize(
    (
        "value",
        "error",
    ),
    (
        ("aaa", True),
        ("0", True),
        ("65536", True),
        ("1", False),
        ("65535", False),
        (1, False),
        (65535, False),
    ),
)
def test_settings_exporter_port(value: str, error: bool):
    if error:
        with pytest.raises((ValueError, ValidationError)):
            Settings(EXPORTER_PORT=value)
    else:
        Settings(EXPORTER_PORT=value)


@pytest.mark.parametrize(
    (
        "value",
        "expected_values",
        "error",
    ),
    (
        ("aaa", None, True),
        ("", [], False),
        ("https://sentry.com", None, True),
        ("[https://sentry.com , sentry.com]", None, True),
        (
            "[https://sentry.com , https://sentry.com]",
            ["https://sentry.com", "https://sentry.com"],
            False,
        ),
        (
            "[https://sentry.com, https://sentry.com]",
            ["https://sentry.com", "https://sentry.com"],
            False,
        ),
        (
            "[https://sentry.com ,https://sentry.com]",
            ["https://sentry.com", "https://sentry.com"],
            False,
        ),
        (
            "[https://sentry.com,https://sentry.com]",
            ["https://sentry.com", "https://sentry.com"],
            False,
        ),
    ),
)
def test_settings_cors_origins(value: str, expected_values: List[HttpUrl], error: bool):
    if error:
        with pytest.raises((ValueError, ValidationError)):
            Settings(BACKEND_CORS_ORIGINS=value)
    else:
        s = Settings(BACKEND_CORS_ORIGINS=value)
        assert s.BACKEND_CORS_ORIGINS == expected_values


@pytest.mark.parametrize(
    (
        "value",
        "error",
    ),
    (
        ("aaa", True),
        ("https://sentry.com", False),
        ("", False),
    ),
)
def test_settings_sentry_dsn(value: str, error: bool):
    if error:
        with pytest.raises(ValidationError):
            Settings(SENTRY_DSN=value)
    else:
        s = Settings(SENTRY_DSN=value)
        if len(value) == 0:
            assert s.SENTRY_DSN is None
        else:
            assert s.SENTRY_DSN == value
