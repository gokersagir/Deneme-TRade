from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ScanResult:
    symbol: str
    scan_date: date
    close: float
    signal: str
    buy_level: float | None
    sell_level: float | None
    stop_loss: float | None
    indicators: dict[str, float]
    note: str
