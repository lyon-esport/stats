import importlib.metadata

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from prometheus_client import start_http_server
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from tortoise.contrib.fastapi import register_tortoise

from les_stats.config import settings
from les_stats.routers.api import api_router

TITLE = "Lyon e-Sport stats"
MODULE_NAME = __name__.split(".")[0]
VERSION = importlib.metadata.version(MODULE_NAME)


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

    application.include_router(api_router)

    return application


app = create_app()

app.mount("/static", StaticFiles(directory="les_stats/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        title=TITLE,
        openapi_url="/openapi.json",
        swagger_favicon_url="/static/favicon.ico"
    )


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.5,
        release=VERSION,
    )
    app.add_middleware(SentryAsgiMiddleware)

models = [f"{MODULE_NAME}.models"]

register_tortoise(
    app,
    db_url=settings.DB_URL,
    modules={"models": models},
    generate_schemas=True,
)


@app.on_event("startup")
async def startup_event():
    start_http_server(settings.EXPORTER_PORT)
