"""FastAPI application entrypoint for the GOROS backend."""

from __future__ import annotations

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.middleware import register_middleware
from app.modules import PUBLIC_ROUTERS, VERSIONED_ROUTERS


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        debug=settings.debug,
        lifespan=lifespan,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_tags=[
            {
                "name": "System",
                "description": "Operational endpoints for health and readiness checks.",
            }
        ],
        contact={
            "name": settings.openapi_contact_name,
            "email": settings.openapi_contact_email,
        },
        license_info={
            "name": settings.openapi_license_name,
            "url": str(settings.openapi_license_url),
        },
        summary="Enterprise AI Operating System backend foundation.",
    )
    register_middleware(app)
    register_exception_handlers(app)

    for router in PUBLIC_ROUTERS:
        app.include_router(router)
    for router in VERSIONED_ROUTERS:
        app.include_router(router, prefix=settings.api_prefix)

    return app


app = create_app()
