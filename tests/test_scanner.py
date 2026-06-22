from __future__ import annotations

from datetime import datetime, timedelta

from trade_reporter.report import render_markdown
from trade_reporter.scanner import normalize_symbol, scan_symbol


def sample_rows() -> list[dict[str, float | datetime]]:
    start = datetime(2025, 1, 1)
    rows = []
    for index in range(45):
        value = 10 + index * 0.2
        rows.append(
            {
                "Date": start + timedelta(days=index),
                "Open": value - 0.1,
                "High": value + 0.3,
                "Low": value - 0.4,
                "Close": value,
            }
        )
    return rows


def test_normalize_symbol_adds_borsa_istanbul_suffix() -> None:
    assert normalize_symbol("thyao") == "THYAO.IS"
    assert normalize_symbol("GARAN.IS") == "GARAN.IS"


def test_scan_symbol_returns_levels_and_signal() -> None:
    result = scan_symbol("THYAO", sample_rows())
    assert result.symbol == "THYAO.IS"
    assert result.buy_level is not None
    assert result.sell_level is not None
    assert result.signal in {"AL", "SAT/UZAK DUR", "İZLE"}


def test_render_markdown_contains_report_columns() -> None:
    report = render_markdown([scan_symbol("THYAO", sample_rows())])
    assert "Alım yeri" in report
    assert "Satım yeri" in report
    assert "THYAO.IS" in report
