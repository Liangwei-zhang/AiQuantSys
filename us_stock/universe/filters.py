from dataclasses import dataclass

from us_stock.universe.models import StockCandidate, StockFilterResult


@dataclass(frozen=True)
class StockUniverseFilterConfig:
    min_price: float = 5.0
    min_avg_dollar_volume_20d: float = 50_000_000.0
    allowed_exchanges: tuple[str, ...] = ("NYSE", "NASDAQ", "ARCA")
    max_spread_bps: float = 20.0


class StockUniverseFilter:
    """Filter tradable US stock candidates for the MVP watchlist."""

    def __init__(self, config: StockUniverseFilterConfig | None = None) -> None:
        self.config = config or StockUniverseFilterConfig()

    def evaluate(self, stock: StockCandidate) -> StockFilterResult:
        reasons: list[str] = []

        if stock.price < self.config.min_price:
            reasons.append("price_below_minimum")

        if stock.avg_dollar_volume_20d < self.config.min_avg_dollar_volume_20d:
            reasons.append("liquidity_below_minimum")

        if not stock.is_active:
            reasons.append("symbol_inactive")

        if stock.exchange not in self.config.allowed_exchanges:
            reasons.append("exchange_not_allowed")

        if stock.is_halted:
            reasons.append("symbol_halted")

        if stock.earnings_blackout:
            reasons.append("earnings_blackout")

        if stock.spread_bps is not None and stock.spread_bps > self.config.max_spread_bps:
            reasons.append("spread_too_wide")

        return StockFilterResult(symbol=stock.symbol, eligible=not reasons, reject_reasons=reasons)

    def filter(self, candidates: list[StockCandidate]) -> list[StockCandidate]:
        return [stock for stock in candidates if self.evaluate(stock).eligible]
