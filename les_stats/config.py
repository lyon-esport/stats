from typing import List, Optional

from pydantic import BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    DB_URL: str
    EXPORTER_PORT: int = 9345
    VALORANT_API_KEY: str
    VALORANT_API_ROUTING: str
    BACKEND_CORS_ORIGINS: List[HttpUrl] = ""
    SENTRY_DSN: Optional[HttpUrl] = ""

    @validator("EXPORTER_PORT", pre=True)
    def check_exporter_port_is_valid(cls, v: str):
        v = int(v)
        if not 1 <= v <= 65535:
            return ValueError(v)
        return v

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str) -> List[HttpUrl]:
        if v.startswith("[") and v.endswith("]"):
            return [i.strip() for i in v[1:-1].split(",")]
        elif len(v) == 0:
            return []
        return ValueError(v)

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    class Config:
        env_prefix = "LES_STATS_"
        env_file = ".env"
