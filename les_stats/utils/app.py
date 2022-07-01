from fastapi import FastAPI

from les_stats.routers.api import api_router


def create_app(title: str, version: str) -> FastAPI:
    application = FastAPI(
        title=title,
        description="Statistics for games",
        version=version,
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
