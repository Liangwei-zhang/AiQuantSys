from datetime import datetime

from fastapi import APIRouter

from app.config import get_settings
from us_stock.api.broker_routes import router as broker_router
from us_stock.calendar.market_calendar import MarketCalendarService
from us_stock.calendar.session_state import MarketSessionState

router = APIRouter()
router.include_router(broker_router)


@router.get("/session", response_model=MarketSessionState)
async def get_market_session() -> MarketSessionState:
    """Return the current MVP US equity session state."""

    settings = get_settings()
    calendar = MarketCalendarService(timezone=settings.default_timezone)
    return calendar.classify()


@router.get("/session/at", response_model=MarketSessionState)
async def get_market_session_at(timestamp: datetime) -> MarketSessionState:
    """Classify a provided timestamp for tests and diagnostics."""

    settings = get_settings()
    calendar = MarketCalendarService(timezone=settings.default_timezone)
    return calendar.classify(timestamp)
