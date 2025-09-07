# app/services/indicators.py
from __future__ import annotations
from collections import deque
from typing import Iterable, List, Dict, Tuple, Optional
from math import sqrt

# Helpers return lists of (ts, value) aligned to input order
# Input closes: list[tuple[datetime, float]]

def sma(closes: List[Tuple], window: int) -> List[Tuple]:
    if window <= 0:
        return []
    out: List[Tuple] = []
    q: deque = deque()
    s = 0.0
    for ts, c in closes:
        q.append(c)
        s += c
        if len(q) > window:
            s -= q.popleft()
        if len(q) == window:
            out.append((ts, s / window))
        else:
            out.append((ts, None))
    return out

def ema(closes: List[Tuple], window: int) -> List[Tuple]:
    if window <= 0:
        return []
    out: List[Tuple] = []
    k = 2.0 / (window + 1.0)
    ema_val: Optional[float] = None
    for ts, c in closes:
        if ema_val is None:
            ema_val = c  # seed with first value; or could use SMA of first window
        else:
            ema_val = c * k + ema_val * (1 - k)
        out.append((ts, ema_val))
    return out

def rsi(closes: List[Tuple], period: int = 14) -> List[Tuple]:
    if period <= 0:
        return []
    out: List[Tuple] = []
    gains: deque = deque(maxlen=period)
    losses: deque = deque(maxlen=period)
    prev: Optional[float] = None
    avg_gain: Optional[float] = None
    avg_loss: Optional[float] = None

    for ts, c in closes:
        if prev is None:
            out.append((ts, None))
            prev = c
            continue

        change = c - prev
        prev = c
        gain = max(change, 0.0)
        loss = max(-change, 0.0)

        if avg_gain is None:  # warm-up first 'period' samples
            gains.append(gain)
            losses.append(loss)
            if len(gains) < period:
                out.append((ts, None))
                continue
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
        else:
            # Wilder's smoothing
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            out.append((ts, 100.0))
        else:
            rs = avg_gain / avg_loss
            out.append((ts, 100.0 - (100.0 / (1.0 + rs))))
    return out
