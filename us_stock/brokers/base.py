from abc import ABC, abstractmethod
from datetime import datetime

from us_stock.brokers.models import (
    AccountSnapshot,
    BarSnapshot,
    OrderRequest,
    OrderResult,
    PositionSnapshot,
    QuoteSnapshot,
)


class BrokerError(RuntimeError):
    pass


class BrokerConfigurationError(BrokerError):
    pass


class BaseBroker(ABC):
    """Abstract broker adapter used by the execution layer."""

    name: str

    @abstractmethod
    async def get_account(self) -> AccountSnapshot:
        raise NotImplementedError

    @abstractmethod
    async def get_positions(self) -> list[PositionSnapshot]:
        raise NotImplementedError

    @abstractmethod
    async def get_quote(self, symbol: str) -> QuoteSnapshot:
        raise NotImplementedError

    @abstractmethod
    async def get_bars(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
        limit: int | None = None,
    ) -> list[BarSnapshot]:
        raise NotImplementedError

    @abstractmethod
    async def submit_order(self, order: OrderRequest) -> OrderResult:
        raise NotImplementedError

    @abstractmethod
    async def cancel_order(self, broker_order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
