from app.config import Settings
from us_stock.brokers.alpaca import AlpacaBroker
from us_stock.brokers.models import OrderStatus


def _broker() -> AlpacaBroker:
    settings = Settings(ALPACA_API_KEY="key", ALPACA_SECRET_KEY="secret")
    return AlpacaBroker(settings)


def test_parse_order_result_maps_filled_status() -> None:
    broker = _broker()
    data = {
        "id": "order-1",
        "status": "filled",
        "symbol": "MSFT",
        "side": "buy",
        "qty": "10",
        "filled_qty": "10",
    }

    result = broker._parse_order_result(data)

    assert result.broker == "alpaca"
    assert result.broker_order_id == "order-1"
    assert result.status == OrderStatus.FILLED
    assert result.symbol == "MSFT"
    assert result.quantity == 10
    assert result.filled_quantity == 10


def test_parse_position_result() -> None:
    broker = _broker()
    data = {
        "symbol": "AAPL",
        "qty": "5",
        "side": "long",
        "avg_entry_price": "180.5",
        "current_price": "182.0",
        "market_value": "910",
        "unrealized_pl": "7.5",
        "unrealized_plpc": "0.0083",
    }

    result = broker._parse_position(data)

    assert result.symbol == "AAPL"
    assert result.quantity == 5
    assert result.avg_entry_price == 180.5
    assert result.market_price == 182.0
    assert result.unrealized_pnl == 7.5
