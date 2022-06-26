import importlib.metadata

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from prometheus_client import start_http_server
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from tortoise.contrib.fastapi import register_tortoise

from les_stats.config import Settings
from les_stats.routers.api import api_router

TITLE = "Lyon e-Sport stats API"
VERSION = importlib.metadata.version("les_stats")


def get_settings() -> Settings:
    return Settings()


def create_app() -> FastAPI:
    application = FastAPI(
        title=TITLE,
        description="Statistics for games",
        version=VERSION,
        contact={
            "name": "Lyon e-Sport",
            "url": "https://www.lyon-esport.fr/contact/",
            "email": "dev@lyon-esport.fr",
        },
        license_info={
            "name": "CeCILL-2.1",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        docs_url=None,
        redoc_url=None,
    )

    return application


if __name__ == "__main__":
    app = create_app()

    app.include_router(api_router)

    app.mount("/static", StaticFiles(directory="les_stats/static"), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in get_settings().BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if get_settings().SENTRY_DSN:
        sentry_sdk.init(
            dsn=get_settings().SENTRY_DSN,
            traces_sample_rate=0.5,
            release=VERSION,
        )
        app.add_middleware(SentryAsgiMiddleware)

    register_tortoise(
        app,
        db_url=get_settings().DB_URL,
        modules={"models": ["les_stats.models"]},
        generate_schemas=True,
    )

    @app.get("/docs", include_in_schema=False)
    async def swagger_ui_html():
        return get_swagger_ui_html(
            title=TITLE,
            openapi_url="/openapi.json",
            swagger_favicon_url="/static/favicon.ico",
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        )

    @app.on_event("startup")
    async def startup_event():
        start_http_server(get_settings().EXPORTER_PORT)

    uvicorn.run(app, host=get_settings().APP_HOST, port=get_settings().APP_PORT)
