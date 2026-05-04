from pydantic import BaseModel, Field


class StockCandidate(BaseModel):
    symbol: str
    name: str | None = None
    exchange: str
    price: float
    avg_dollar_volume_20d: float
    is_active: bool = True
    is_halted: bool = False
    earnings_blackout: bool = False
    spread_bps: float | None = None
    sector: str | None = None
    industry: str | None = None


class StockFilterResult(BaseModel):
    symbol: str
    eligible: bool
    reject_reasons: list[str] = Field(default_factory=list)


class StockScore(BaseModel):
    symbol: str
    score: float
    liquidity_score: float
    relative_strength_score: float
    trend_quality_score: float
    volatility_score: float
    earnings_safety_score: float
    sector_strength_score: float
    option_sentiment_score: float = 0.0
