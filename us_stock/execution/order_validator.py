from pydantic import BaseModel, Field

from app.config import Settings
from us_stock.brokers.models import OrderRequest, OrderType
from us_stock.calendar.session_state import MarketSessionState


class OrderValidationResult(BaseModel):
    accepted: bool
    reject_reasons: list[str] = Field(default_factory=list)


class BasicOrderValidator:
    """Conservative MVP order validator."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate(self, order: OrderRequest, session_state: MarketSessionState) -> OrderValidationResult:
        reasons: list[str] = []

        if not self.settings.allow_live_trading:
            # This project currently targets Alpaca paper trading only.
            pass

        if not session_state.is_trading_allowed:
            reasons.append("trading_not_allowed_in_current_session")

        if not session_state.allow_new_positions:
            reasons.append("new_positions_not_allowed_in_current_session")

        if order.extended_hours and not self.settings.allow_extended_hours:
            reasons.append("extended_hours_disabled")

        if order.order_type == OrderType.MARKET and order.extended_hours:
            reasons.append("market_order_not_allowed_extended_hours")

        if order.order_type in {OrderType.LIMIT, OrderType.STOP_LIMIT} and order.limit_price is None:
            reasons.append("limit_price_required")

        if order.order_type in {OrderType.STOP, OrderType.STOP_LIMIT} and order.stop_price is None:
            reasons.append("stop_price_required")

        if order.quantity <= 0:
            reasons.append("quantity_must_be_positive")

        return OrderValidationResult(accepted=not reasons, reject_reasons=reasons)
