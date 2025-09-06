from __future__ import annotations
import httpx
from datetime import datetime, date
from typing import List, Dict, Optional
from services.market_data.base import MarketDataProvider, PriceBar, InstrumentInfo

BASE_URL = "https://www.alphavantage.co/query"

class AlphaVantageProvider(MarketDataProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ALPHA_VANTAGE_KEY is required for alpha_vantage provider")
        self.key = api_key
        self.client = httpx.Client(timeout=30)

    def _get(self, params: Dict[str, str]) -> Dict:
        params = {**params, "apikey": self.key}
        r = self.client.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()
        if any(k in data for k in ["Error Message", "Information", "Note"]):
            # AV returns friendly throttling messages under these keys
            raise RuntimeError(data.get("Error Message") or data.get("Information") or data.get("Note"))
        return data

    def search(self, query: str, limit: int = 5) -> List[InstrumentInfo]:
        data = self._get({"function": "SYMBOL_SEARCH", "keywords": query})
        matches = data.get("bestMatches", [])
        out: List[InstrumentInfo] = []
        for m in matches[:limit]:
            out.append({
                "symbol": m.get("1. symbol"),
                "name": m.get("2. name"),
                "exchange": m.get("4. region"),
                "currency": m.get("8. currency"),
                "asset_class": None,
                "sector": None,
                "industry": None,
            })
        return out

    def daily_prices(self, symbol: str, start: Optional[date] = None, end: Optional[date] = None) -> List[PriceBar]:
        data = self._get({
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
        })
        series = data.get("Time Series (Daily)", {})
        rows: List[PriceBar] = []
        for k, v in series.items():
            ts = datetime.strptime(k, "%Y-%m-%d")
            if start and ts.date() < start:
                continue
            if end and ts.date() > end:
                continue
            rows.append({
                "ts": ts,
                "open": float(v["1. open"]),
                "high": float(v["2. high"]),
                "low": float(v["3. low"]),
                "close": float(v["4. close"]),
                "volume": int(v.get("6. volume", 0)),
            })
        rows.sort(key=lambda r: r["ts"])  # ascending time
        return rows