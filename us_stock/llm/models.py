from enum import Enum
from pydantic import BaseModel, Field


class TradeAction(str, Enum):
    OPEN_LONG_LIMIT = "open_long_limit"
    CLOSE_POSITION = "close_position"
    UPDATE_STOP_LOSS = "update_stop_loss"
    WAIT = "wait"
    HOLD = "hold"


class StrategyType(str, Enum):
    TREND_FOLLOWING = "trend_following"
    PULLBACK = "pullback"
    BREAKOUT = "breakout"
    GAP_FOLLOW = "gap_follow"
    NO_TRADE = "no_trade"


class LLMDecision(BaseModel):
    symbol: str
    action: TradeAction
    strategy_type: StrategyType
    confidence: float = Field(ge=0.0, le=1.0)
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    position_size_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    reason: str
    risk_notes: list[str] = Field(default_factory=list)
    must_pass_checks: list[str] = Field(default_factory=list)


class DecisionValidationResult(BaseModel):
    accepted: bool
    decision: LLMDecision | None = None
    reject_reason: str | None = None
