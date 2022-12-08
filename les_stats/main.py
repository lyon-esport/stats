import importlib.metadata
import logging

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from prometheus_client import start_http_server
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from tortoise.contrib.fastapi import register_tortoise

from les_stats.metrics.main import init_metrics
from les_stats.routers.api import api_router
from les_stats.utils.config import get_settings

title = "Lyon e-Sport stats API"
version = importlib.metadata.version("les_stats")


def create_app() -> FastAPI:
    application = FastAPI(
        title=title,
        description="Statistics for games see https://github.com/lyon-esport/stats",
        version=version,
        contact={
            "name": "Lyon e-Sport",
            "url": "https://www.lyon-esport.fr/",
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


if __name__ == "__main__":
    logger = logging.getLogger("uvicorn")

    app = create_app()
    app.mount("/static", StaticFiles(packages=["les_stats"]), name="static")

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
            integrations=[StarletteIntegration(), FastApiIntegration()],
            traces_sample_rate=0.5,
            release=version,
        )

    register_tortoise(
        app,
        db_url=get_settings().DB_URL,
        modules={"models": ["les_stats.models"]},
        generate_schemas=True,
    )

    @app.get("/docs", include_in_schema=False)
    async def swagger_ui_html():
        return get_swagger_ui_html(
            title=title,
            openapi_url="/openapi.json",
            swagger_favicon_url="/static/favicon.ico",
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        )

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"App version {version}")
        await init_metrics()
        start_http_server(
            addr=get_settings().EXPORTER_ADDR, port=get_settings().EXPORTER_PORT
        )
        logger.info(
            f"Exporter running on http://{get_settings().EXPORTER_ADDR}:{get_settings().EXPORTER_PORT}"
        )

    uvicorn.run(app, host=get_settings().APP_HOST, port=get_settings().APP_PORT)
