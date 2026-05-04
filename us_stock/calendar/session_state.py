from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MarketSession(str, Enum):
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    OPEN_AUCTION = "open_auction"
    REGULAR = "regular"
    CLOSE_AUCTION = "close_auction"
    AFTER_HOURS = "after_hours"
    HALF_DAY = "half_day"
    HALTED = "halted"


class MarketSessionState(BaseModel):
    """Normalized US equity market session state."""

    session: MarketSession
    timestamp: datetime
    timezone: str = "America/New_York"
    is_trading_allowed: bool = False
    reason: str | None = None
    allow_new_positions: bool = False
    allow_position_reduction: bool = True
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)
