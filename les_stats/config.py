from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    DB_URL: str
    EXPORTER_PORT: int = 9345
    VALORANT_API_KEY: str
    VALORANT_API_ROUTING: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    SENTRY_DSN: Optional[HttpUrl] = ""

    @validator("EXPORTER_PORT", pre=True)
    def check_exporter_port_is_valid(cls, v: str):
        v = int(v)
        if not 1 <= v <= 65535:
            ValueError(v)
        return v

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    class Config:
        env_file = ".env"


settings = Settings()
