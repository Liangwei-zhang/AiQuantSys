from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
    SELL_SHORT = "sell_short"
    BUY_TO_COVER = "buy_to_cover"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class TimeInForce(str, Enum):
    DAY = "day"
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"


class OrderStatus(str, Enum):
    NEW = "new"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


class AccountSnapshot(BaseModel):
    broker: str
    account_id: str | None = None
    status: str | None = None
    currency: str = "USD"
    equity: float
    cash: float
    buying_power: float
    daytrade_count: int | None = None
    pattern_day_trader: bool | None = None
    raw: dict = Field(default_factory=dict)


class PositionSnapshot(BaseModel):
    symbol: str
    quantity: float
    side: str
    avg_entry_price: float
    market_price: float | None = None
    market_value: float | None = None
    unrealized_pnl: float | None = None
    unrealized_pnl_pct: float | None = None
    raw: dict = Field(default_factory=dict)


class QuoteSnapshot(BaseModel):
    symbol: str
    bid_price: float | None = None
    bid_size: float | None = None
    ask_price: float | None = None
    ask_size: float | None = None
    timestamp: datetime | None = None
    raw: dict = Field(default_factory=dict)

    @property
    def spread_bps(self) -> float | None:
        if not self.bid_price or not self.ask_price:
            return None
        mid = (self.bid_price + self.ask_price) / 2
        if mid <= 0:
            return None
        return (self.ask_price - self.bid_price) / mid * 10_000


class BarSnapshot(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float | None = None
    trade_count: int | None = None
    raw: dict = Field(default_factory=dict)


class OrderRequest(BaseModel):
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.LIMIT
    time_in_force: TimeInForce = TimeInForce.DAY
    limit_price: float | None = None
    stop_price: float | None = None
    extended_hours: bool = False
    client_order_id: str | None = None


class OrderResult(BaseModel):
    broker: str
    broker_order_id: str | None = None
    status: OrderStatus = OrderStatus.UNKNOWN
    symbol: str
    side: OrderSide
    quantity: float
    filled_quantity: float | None = None
    submitted_at: datetime | None = None
    filled_at: datetime | None = None
    raw: dict = Field(default_factory=dict)
