from app.config import Settings, get_settings
from us_stock.brokers.alpaca import AlpacaBroker
from us_stock.brokers.base import BaseBroker, BrokerConfigurationError


SUPPORTED_BROKERS = {"alpaca"}


def create_broker(name: str = "alpaca", settings: Settings | None = None) -> BaseBroker:
    normalized = name.lower().strip()
    runtime_settings = settings or get_settings()

    if normalized == "alpaca":
        return AlpacaBroker(runtime_settings)

    raise BrokerConfigurationError(f"unsupported_broker:{name}")
