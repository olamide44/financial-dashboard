from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import date

PriceBar = Dict[str, object]  # {"ts": datetime, "open": float, "high": float, "low": float, "close": float, "volume": int|None}
InstrumentInfo = Dict[str, object]  # {"symbol": str, "exchange": str|None, "name": str|None, ...}

class MarketDataProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[InstrumentInfo]:
        ...

    @abstractmethod
    def daily_prices(self, symbol: str, start: Optional[date] = None, end: Optional[date] = None) -> List[PriceBar]:
        ...