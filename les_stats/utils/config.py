from typing import Any, List, Optional, Union

import pytz
from pydantic import BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    TIMEZONE: str
    DB_URL: str
    SALT: str
    EXPORTER_ADDR: str = "127.0.0.1"
    EXPORTER_PORT: int = 9345
    VALORANT_API_KEY: str = None
    VALORANT_API_ROUTING: str = None
    TFT_API_KEY: str = None
    TFT_API_ROUTING: str = None
    LOL_API_KEY: str = None
    LOL_API_ROUTING: str = None
    BACKEND_CORS_ORIGINS: List[HttpUrl] = []
    SENTRY_DSN: Optional[HttpUrl] = ""

    @validator("APP_PORT", "EXPORTER_PORT", pre=True, allow_reuse=True)
    def check_port_is_valid(cls, v: str) -> int:
        v = int(v)
        if not 1 <= v <= 65535:
            return ValueError(v)
        return v

    @validator("TIMEZONE", pre=True)
    def check_timezone_is_valid(cls, v: str) -> str:
        if v not in pytz.all_timezones:
            raise ValueError("Invalid timezone")
        return v

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[List, str]) -> List[HttpUrl]:
        if isinstance(v, list):
            return v
        else:
            return [] if len(v) == 0 else [i.strip() for i in v.split(",")]

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[HttpUrl]:
        if len(v) == 0:
            return None
        return v

    class Config:
        env_prefix = "LES_STATS_"
        env_file = ".env"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == "BACKEND_CORS_ORIGINS":
                return (
                    [] if len(raw_val) == 0 else [x.strip() for x in raw_val.split(",")]
                )
            return cls.json_loads(raw_val)


def get_settings() -> Settings:
    return Settings()
