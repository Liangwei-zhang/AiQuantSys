from fastapi import FastAPI

from app.config import get_settings
from app.logging_config import configure_logging
from us_stock.api.routes import router as us_stock_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, version="0.1.0")

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name, "env": settings.app_env}

    app.include_router(us_stock_router, prefix="/api/us-stock", tags=["us-stock"])
    return app


app = create_app()
