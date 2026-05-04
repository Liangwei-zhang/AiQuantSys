from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query

from us_stock.brokers.base import BrokerConfigurationError, BrokerError
from us_stock.brokers.factory import create_broker
from us_stock.brokers.models import AccountSnapshot, BarSnapshot, PositionSnapshot, QuoteSnapshot

router = APIRouter(prefix="/broker", tags=["broker"])


@router.get("/account", response_model=AccountSnapshot)
async def get_broker_account(broker: str = "alpaca") -> AccountSnapshot:
    adapter = None
    try:
        adapter = create_broker(broker)
        return await adapter.get_account()
    except BrokerConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except BrokerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        if adapter:
            await adapter.close()


@router.get("/positions", response_model=list[PositionSnapshot])
async def get_broker_positions(broker: str = "alpaca") -> list[PositionSnapshot]:
    adapter = None
    try:
        adapter = create_broker(broker)
        return await adapter.get_positions()
    except BrokerConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except BrokerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        if adapter:
            await adapter.close()


@router.get("/quote/{symbol}", response_model=QuoteSnapshot)
async def get_broker_quote(symbol: str, broker: str = "alpaca") -> QuoteSnapshot:
    adapter = None
    try:
        adapter = create_broker(broker)
        return await adapter.get_quote(symbol.upper())
    except BrokerConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except BrokerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        if adapter:
            await adapter.close()


@router.get("/bars/{symbol}", response_model=list[BarSnapshot])
async def get_broker_bars(
    symbol: str,
    broker: str = "alpaca",
    timeframe: str = Query(default="15Min"),
    lookback_days: int = Query(default=5, ge=1, le=365),
    limit: int | None = Query(default=None, ge=1, le=10_000),
) -> list[BarSnapshot]:
    adapter = None
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    try:
        adapter = create_broker(broker)
        return await adapter.get_bars(symbol.upper(), timeframe, start, end, limit=limit)
    except BrokerConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except BrokerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        if adapter:
            await adapter.close()
