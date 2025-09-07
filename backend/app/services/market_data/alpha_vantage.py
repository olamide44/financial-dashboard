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
        """
        Fetch daily OHLCV. Try ADJUSTED first; if AV says 'premium' or similar, fall back to DAILY.
        """
        funcs = ["TIME_SERIES_DAILY_ADJUSTED", "TIME_SERIES_DAILY"]
        last_err: Exception | None = None

        for fn in funcs:
            try:
                data = self._get({
                    "function": fn,
                    "symbol": symbol,
                    "outputsize": "full",
                })
                series = data.get("Time Series (Daily)", {})
                if not isinstance(series, dict) or not series:
                    raise RuntimeError(f"No daily data in response for {symbol} ({fn})")

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
                rows.sort(key=lambda r: r["ts"])
                return rows
            except Exception as e:
                # Keep the last error; try the next function as a fallback
                last_err = e
                continue

        # If both calls failed, raise the last one
        assert last_err is not None
        raise last_err