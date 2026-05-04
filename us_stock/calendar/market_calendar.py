from datetime import datetime, time
from zoneinfo import ZoneInfo

from us_stock.calendar.session_state import MarketSession, MarketSessionState


class MarketCalendarService:
    """Basic US market session classifier.

    This MVP implementation handles regular weekdays and core session windows.
    Holiday and half-day calendars should be backed by exchange calendars in Phase 2.
    """

    def __init__(self, timezone: str = "America/New_York") -> None:
        self.timezone = timezone
        self.tzinfo = ZoneInfo(timezone)

    def classify(self, now: datetime | None = None) -> MarketSessionState:
        current = now.astimezone(self.tzinfo) if now else datetime.now(self.tzinfo)

        if current.weekday() >= 5:
            return MarketSessionState(
                session=MarketSession.CLOSED,
                timestamp=current,
                timezone=self.timezone,
                reason="weekend",
                is_trading_allowed=False,
                allow_new_positions=False,
            )

        current_time = current.time()

        if time(4, 0) <= current_time < time(9, 25):
            session = MarketSession.PRE_MARKET
            return MarketSessionState(
                session=session,
                timestamp=current,
                timezone=self.timezone,
                reason="pre_market_mvp_read_only",
                is_trading_allowed=False,
                allow_new_positions=False,
            )

        if time(9, 25) <= current_time < time(9, 31):
            return MarketSessionState(
                session=MarketSession.OPEN_AUCTION,
                timestamp=current,
                timezone=self.timezone,
                reason="open_protection_window",
                is_trading_allowed=False,
                allow_new_positions=False,
            )

        if time(9, 31) <= current_time < time(15, 45):
            return MarketSessionState(
                session=MarketSession.REGULAR,
                timestamp=current,
                timezone=self.timezone,
                is_trading_allowed=True,
                allow_new_positions=True,
            )

        if time(15, 45) <= current_time < time(16, 0):
            return MarketSessionState(
                session=MarketSession.CLOSE_AUCTION,
                timestamp=current,
                timezone=self.timezone,
                reason="close_protection_window",
                is_trading_allowed=True,
                allow_new_positions=False,
            )

        if time(16, 0) <= current_time < time(20, 0):
            return MarketSessionState(
                session=MarketSession.AFTER_HOURS,
                timestamp=current,
                timezone=self.timezone,
                reason="after_hours_mvp_read_only",
                is_trading_allowed=False,
                allow_new_positions=False,
            )

        return MarketSessionState(
            session=MarketSession.CLOSED,
            timestamp=current,
            timezone=self.timezone,
            reason="outside_us_equity_session",
            is_trading_allowed=False,
            allow_new_positions=False,
        )
