from us_stock.universe.filters import StockUniverseFilter
from us_stock.universe.models import StockCandidate


def test_high_quality_stock_is_eligible() -> None:
    stock = StockCandidate(
        symbol="MSFT",
        exchange="NASDAQ",
        price=420,
        avg_dollar_volume_20d=5_000_000_000,
        spread_bps=2.5,
    )

    result = StockUniverseFilter().evaluate(stock)

    assert result.eligible is True
    assert result.reject_reasons == []


def test_low_liquidity_stock_is_rejected() -> None:
    stock = StockCandidate(
        symbol="TEST",
        exchange="NASDAQ",
        price=10,
        avg_dollar_volume_20d=1_000_000,
        spread_bps=5,
    )

    result = StockUniverseFilter().evaluate(stock)

    assert result.eligible is False
    assert "liquidity_below_minimum" in result.reject_reasons
