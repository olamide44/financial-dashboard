from core.config import settings
from .alpha_vantage import AlphaVantageProvider
from .base import MarketDataProvider
from core.config import settings

_provider: MarketDataProvider | None = None

def get_provider() -> MarketDataProvider:
    global _provider
    if _provider:
        return _provider
    if settings.use_provider == "alpha_vantage":
        _provider = AlphaVantageProvider(settings.alpha_vantage_key)
        return _provider
    raise ValueError(f"Unsupported provider: {settings.use_provider}")