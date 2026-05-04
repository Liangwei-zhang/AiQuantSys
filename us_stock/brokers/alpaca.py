from datetime import datetime
from typing import Any

import httpx

from app.config import Settings
from us_stock.brokers.base import BaseBroker, BrokerConfigurationError, BrokerError
from us_stock.brokers.models import (
    AccountSnapshot,
    BarSnapshot,
    OrderRequest,
    OrderResult,
    OrderSide,
    OrderStatus,
    PositionSnapshot,
    QuoteSnapshot,
)


class AlpacaBroker(BaseBroker):
    """Alpaca Paper Trading broker adapter.

    This adapter targets paper trading by default and is intentionally conservative.
    Live trading should be enabled only after explicit product-level controls exist.
    """

    name = "alpaca"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.alpaca_api_key or not settings.alpaca_secret_key:
            raise BrokerConfigurationError("alpaca_credentials_missing")

        self.trading_base_url = settings.alpaca_paper_base_url.rstrip("/")
        self.data_base_url = settings.alpaca_data_base_url.rstrip("/")
        self._external_client = client is not None
        self.client = client or httpx.AsyncClient(timeout=30)
        self.headers = {
            "APCA-API-KEY-ID": settings.alpaca_api_key,
            "APCA-API-SECRET-KEY": settings.alpaca_secret_key,
            "accept": "application/json",
            "content-type": "application/json",
        }

    async def close(self) -> None:
        if not self._external_client:
            await self.client.aclose()

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        response = await self.client.request(
            method,
            url,
            headers=self.headers,
            params=params,
            json=json,
        )
        if response.status_code >= 400:
            raise BrokerError(f"alpaca_request_failed:{response.status_code}:{response.text}")
        return response.json()

    async def get_account(self) -> AccountSnapshot:
        data = await self._request("GET", f"{self.trading_base_url}/v2/account")
        return AccountSnapshot(
            broker=self.name,
            account_id=data.get("id"),
            status=data.get("status"),
            currency=data.get("currency", "USD"),
            equity=float(data.get("equity", 0) or 0),
            cash=float(data.get("cash", 0) or 0),
            buying_power=float(data.get("buying_power", 0) or 0),
            daytrade_count=int(data["daytrade_count"]) if data.get("daytrade_count") is not None else None,
            pattern_day_trader=data.get("pattern_day_trader"),
            raw=data,
        )

    async def get_positions(self) -> list[PositionSnapshot]:
        data = await self._request("GET", f"{self.trading_base_url}/v2/positions")
        return [self._parse_position(item) for item in data]

    async def get_quote(self, symbol: str) -> QuoteSnapshot:
        data = await self._request(
            "GET",
            f"{self.data_base_url}/v2/stocks/{symbol}/quotes/latest",
        )
        quote = data.get("quote", {})
        return QuoteSnapshot(
            symbol=symbol.upper(),
            bid_price=_float_or_none(quote.get("bp")),
            bid_size=_float_or_none(quote.get("bs")),
            ask_price=_float_or_none(quote.get("ap")),
            ask_size=_float_or_none(quote.get("as")),
            timestamp=_parse_datetime(quote.get("t")),
            raw=data,
        )

    async def get_bars(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
        limit: int | None = None,
    ) -> list[BarSnapshot]:
        params: dict[str, Any] = {
            "timeframe": timeframe,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "adjustment": "all",
        }
        if limit is not None:
            params["limit"] = limit

        data = await self._request(
            "GET",
            f"{self.data_base_url}/v2/stocks/{symbol}/bars",
            params=params,
        )
        return [self._parse_bar(symbol.upper(), item) for item in data.get("bars", [])]

    async def submit_order(self, order: OrderRequest) -> OrderResult:
        payload: dict[str, Any] = {
            "symbol": order.symbol.upper(),
            "qty": str(order.quantity),
            "side": order.side.value,
            "type": order.order_type.value,
            "time_in_force": order.time_in_force.value,
            "extended_hours": order.extended_hours,
        }
        if order.limit_price is not None:
            payload["limit_price"] = str(order.limit_price)
        if order.stop_price is not None:
            payload["stop_price"] = str(order.stop_price)
        if order.client_order_id:
            payload["client_order_id"] = order.client_order_id

        data = await self._request("POST", f"{self.trading_base_url}/v2/orders", json=payload)
        return self._parse_order_result(data)

    async def cancel_order(self, broker_order_id: str) -> bool:
        await self._request("DELETE", f"{self.trading_base_url}/v2/orders/{broker_order_id}")
        return True

    def _parse_position(self, data: dict[str, Any]) -> PositionSnapshot:
        return PositionSnapshot(
            symbol=data.get("symbol", ""),
            quantity=float(data.get("qty", 0) or 0),
            side=data.get("side", "long"),
            avg_entry_price=float(data.get("avg_entry_price", 0) or 0),
            market_price=_float_or_none(data.get("current_price")),
            market_value=_float_or_none(data.get("market_value")),
            unrealized_pnl=_float_or_none(data.get("unrealized_pl")),
            unrealized_pnl_pct=_float_or_none(data.get("unrealized_plpc")),
            raw=data,
        )

    def _parse_bar(self, symbol: str, data: dict[str, Any]) -> BarSnapshot:
        return BarSnapshot(
            symbol=symbol,
            timestamp=_parse_datetime(data.get("t")) or datetime.utcnow(),
            open=float(data.get("o", 0) or 0),
            high=float(data.get("h", 0) or 0),
            low=float(data.get("l", 0) or 0),
            close=float(data.get("c", 0) or 0),
            volume=float(data.get("v", 0) or 0),
            vwap=_float_or_none(data.get("vw")),
            trade_count=int(data["n"]) if data.get("n") is not None else None,
            raw=data,
        )

    def _parse_order_result(self, data: dict[str, Any]) -> OrderResult:
        status = _map_order_status(data.get("status"))
        side = OrderSide(data.get("side", "buy"))
        return OrderResult(
            broker=self.name,
            broker_order_id=data.get("id"),
            status=status,
            symbol=data.get("symbol", ""),
            side=side,
            quantity=float(data.get("qty", 0) or 0),
            filled_quantity=_float_or_none(data.get("filled_qty")),
            submitted_at=_parse_datetime(data.get("submitted_at")),
            filled_at=_parse_datetime(data.get("filled_at")),
            raw=data,
        )


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _map_order_status(status: str | None) -> OrderStatus:
    match status:
        case "new" | "accepted" | "pending_new":
            return OrderStatus.NEW
        case "filled":
            return OrderStatus.FILLED
        case "partially_filled":
            return OrderStatus.PARTIALLY_FILLED
        case "canceled" | "cancelled":
            return OrderStatus.CANCELED
        case "rejected":
            return OrderStatus.REJECTED
        case _:
            return OrderStatus.UNKNOWN
