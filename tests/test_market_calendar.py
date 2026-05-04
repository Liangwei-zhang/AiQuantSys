from datetime import datetime
from zoneinfo import ZoneInfo

from us_stock.calendar.market_calendar import MarketCalendarService
from us_stock.calendar.session_state import MarketSession


def test_regular_session_allows_new_positions() -> None:
    service = MarketCalendarService()
    state = service.classify(datetime(2026, 5, 4, 10, 0, tzinfo=ZoneInfo("America/New_York")))

    assert state.session == MarketSession.REGULAR
    assert state.is_trading_allowed is True
    assert state.allow_new_positions is True


def test_weekend_is_closed() -> None:
    service = MarketCalendarService()
    state = service.classify(datetime(2026, 5, 3, 10, 0, tzinfo=ZoneInfo("America/New_York")))

    assert state.session == MarketSession.CLOSED
    assert state.is_trading_allowed is False
    assert state.allow_new_positions is False


def test_open_protection_window_blocks_new_positions() -> None:
    service = MarketCalendarService()
    state = service.classify(datetime(2026, 5, 4, 9, 28, tzinfo=ZoneInfo("America/New_York")))

    assert state.session == MarketSession.OPEN_AUCTION
    assert state.is_trading_allowed is False
    assert state.allow_new_positions is False
