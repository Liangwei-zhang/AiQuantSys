from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import Settings
from us_stock.brokers.models import OrderRequest, OrderSide, OrderType
from us_stock.calendar.market_calendar import MarketCalendarService
from us_stock.execution.order_validator import BasicOrderValidator


def _settings() -> Settings:
    return Settings(ALPACA_API_KEY="key", ALPACA_SECRET_KEY="secret")


def test_limit_order_requires_limit_price() -> None:
    session = MarketCalendarService().classify(
        datetime(2026, 5, 4, 10, 0, tzinfo=ZoneInfo("America/New_York"))
    )
    order = OrderRequest(symbol="MSFT", side=OrderSide.BUY, quantity=10, order_type=OrderType.LIMIT)

    result = BasicOrderValidator(_settings()).validate(order, session)

    assert result.accepted is False
    assert "limit_price_required" in result.reject_reasons


def test_valid_regular_session_limit_order_is_accepted() -> None:
    session = MarketCalendarService().classify(
        datetime(2026, 5, 4, 10, 0, tzinfo=ZoneInfo("America/New_York"))
    )
    order = OrderRequest(
        symbol="MSFT",
        side=OrderSide.BUY,
        quantity=10,
        order_type=OrderType.LIMIT,
        limit_price=420,
    )

    result = BasicOrderValidator(_settings()).validate(order, session)

    assert result.accepted is True
    assert result.reject_reasons == []


def test_closed_session_blocks_new_order() -> None:
    session = MarketCalendarService().classify(
        datetime(2026, 5, 3, 10, 0, tzinfo=ZoneInfo("America/New_York"))
    )
    order = OrderRequest(
        symbol="MSFT",
        side=OrderSide.BUY,
        quantity=10,
        order_type=OrderType.LIMIT,
        limit_price=420,
    )

    result = BasicOrderValidator(_settings()).validate(order, session)

    assert result.accepted is False
    assert "trading_not_allowed_in_current_session" in result.reject_reasons
