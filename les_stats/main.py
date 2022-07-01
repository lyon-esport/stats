import importlib.metadata
import logging

import sentry_sdk
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from prometheus_client import start_http_server
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from tortoise.contrib.fastapi import register_tortoise

from les_stats.utils.app import create_app
from les_stats.utils.config import get_settings
from les_stats.utils.metrics import init_metrics

if __name__ == "__main__":
    title = "Lyon e-Sport stats API"
    version = importlib.metadata.version("les_stats")

    logger = logging.getLogger("uvicorn")
    logger.info(f"Starting les_stats v{version}")

    app = create_app(title, version)
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
            release=version,
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
            title=title,
            openapi_url="/openapi.json",
            swagger_favicon_url="/static/favicon.ico",
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        )

    @app.on_event("startup")
    async def startup_event():
        await init_metrics()
        start_http_server(
            addr=get_settings().EXPORTER_ADDR, port=get_settings().EXPORTER_PORT
        )
        logger.info(
            f"Exporter running on http://{get_settings().EXPORTER_ADDR}:{get_settings().EXPORTER_PORT}"
        )

    uvicorn.run(app, host=get_settings().APP_HOST, port=get_settings().APP_PORT)
