from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .indicators import atr, ema, ott_like, supertrend
from .models import ScanResult

REQUIRED_COLUMNS = {"Date", "Open", "High", "Low", "Close"}


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("empty symbol")
    return symbol if symbol.endswith(".IS") else f"{symbol}.IS"


def load_csv(path: Path) -> list[dict[str, float | datetime]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} is empty")
    missing = REQUIRED_COLUMNS - set(rows[0])
    if missing:
        raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")
    parsed = [
        {
            "Date": datetime.fromisoformat(row["Date"]),
            "Open": float(row["Open"]),
            "High": float(row["High"]),
            "Low": float(row["Low"]),
            "Close": float(row["Close"]),
        }
        for row in rows
    ]
    return sorted(parsed, key=lambda row: row["Date"])


def scan_symbol(symbol: str, rows: list[dict[str, float | datetime]]) -> ScanResult:
    if len(rows) < 30:
        raise ValueError(f"{symbol} needs at least 30 rows")
    high = [float(row["High"]) for row in rows]
    low = [float(row["Low"]) for row in rows]
    close = [float(row["Close"]) for row in rows]
    ema_8 = ema(close, 8)
    ema_21 = ema(close, 21)
    atr_10 = atr(high, low, close, 10)
    _basis, ott_line, ott_direction = ott_like(close)
    st_line, st_direction = supertrend(high, low, close)

    latest = -1
    previous = -2
    latest_close = close[latest]
    latest_atr = atr_10[latest] or 0.0
    latest_supertrend = st_line[latest] if st_line[latest] is not None else low[latest]
    buy_level = max(ema_8[latest], ott_line[latest], latest_supertrend)
    sell_level = min(ema_21[latest], ott_line[latest], latest_supertrend)
    stop_loss = latest_close - 2 * latest_atr

    crossed_up = ema_8[previous] <= ema_21[previous] and ema_8[latest] > ema_21[latest]
    crossed_down = ema_8[previous] >= ema_21[previous] and ema_8[latest] < ema_21[latest]
    bullish_stack = latest_close > buy_level and ott_direction[latest] == 1 and st_direction[latest] == 1
    bearish_stack = latest_close < sell_level or ott_direction[latest] == -1 or st_direction[latest] == -1

    if crossed_up or bullish_stack:
        signal = "AL"
        note = "Trend ve kısa ortalama yukarı yönde; kapanış teyidi aranmalı."
    elif crossed_down or bearish_stack:
        signal = "SAT/UZAK DUR"
        note = "Trend zayıf veya satış seviyesi aşağı kırılmış."
    else:
        signal = "İZLE"
        note = "Net al/sat teyidi yok; seviyeler takip edilmeli."

    scan_date = rows[latest]["Date"]
    if not isinstance(scan_date, datetime):
        raise TypeError("Date must be datetime")
    return ScanResult(
        symbol=normalize_symbol(symbol),
        scan_date=scan_date.date(),
        close=round(latest_close, 2),
        signal=signal,
        buy_level=round(buy_level, 2),
        sell_level=round(sell_level, 2),
        stop_loss=round(stop_loss, 2),
        indicators={
            "ema_8": round(ema_8[latest], 2),
            "ema_21": round(ema_21[latest], 2),
            "ott_line": round(ott_line[latest], 2),
            "supertrend_line": round(float(latest_supertrend), 2),
            "atr_10": round(latest_atr, 2),
        },
        note=note,
    )


def scan_csv_directory(data_dir: Path, symbols: list[str]) -> list[ScanResult]:
    results: list[ScanResult] = []
    for symbol in symbols:
        normalized = normalize_symbol(symbol)
        candidates = [data_dir / f"{normalized}.csv", data_dir / f"{normalized.removesuffix('.IS')}.csv"]
        path = next((candidate for candidate in candidates if candidate.exists()), None)
        if path is not None:
            results.append(scan_symbol(normalized, load_csv(path)))
    return results
