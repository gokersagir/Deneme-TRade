from __future__ import annotations

import argparse
from pathlib import Path

from .report import render_markdown
from .scanner import normalize_symbol, scan_csv_directory, scan_symbol


def read_symbols(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def download(symbol: str, period: str):
    try:
        import pandas as pd  # noqa: F401
        import yfinance as yf
    except ImportError as exc:
        raise SystemExit("Canlı veri için `pip install -e .[live]` çalıştırın veya --csv-dir kullanın.") from exc
    frame = yf.download(normalize_symbol(symbol), period=period, interval="1d", auto_adjust=False, progress=False)
    if frame.empty:
        return []
    if hasattr(frame.columns, "levels"):
        frame.columns = frame.columns.get_level_values(0)
    frame = frame.reset_index()
    return [
        {"Date": row.Date.to_pydatetime(), "Open": row.Open, "High": row.High, "Low": row.Low, "Close": row.Close}
        for row in frame.itertuples(index=False)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="BIST 100 günlük alım/satım raporu üretir.")
    parser.add_argument("--symbols-file", type=Path, default=Path("data/bist100_symbols.txt"))
    parser.add_argument("--csv-dir", type=Path, help="İnternetsiz kullanım için OHLC CSV klasörü")
    parser.add_argument("--period", default="1y", help="yfinance veri aralığı")
    parser.add_argument("--output", type=Path, default=Path("reports/bist100_daily.md"))
    args = parser.parse_args()

    symbols = read_symbols(args.symbols_file)
    if args.csv_dir:
        results = scan_csv_directory(args.csv_dir, symbols)
    else:
        results = []
        for symbol in symbols:
            rows = download(symbol, args.period)
            if rows:
                results.append(scan_symbol(symbol, rows))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(results), encoding="utf-8")
    print(f"Rapor yazıldı: {args.output} ({len(results)} hisse)")


if __name__ == "__main__":
    main()
