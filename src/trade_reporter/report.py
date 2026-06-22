from __future__ import annotations

from .models import ScanResult


def render_markdown(results: list[ScanResult]) -> str:
    title_date = results[0].scan_date.isoformat() if results else "veri-yok"
    lines = [
        f"# BIST 100 Günlük Tarama Raporu - {title_date}",
        "",
        "> Bu rapor yatırım tavsiyesi değildir; teknik tarama çıktısıdır.",
        "",
        "| Hisse | Sinyal | Kapanış | Alım yeri | Satım yeri | Stop | Not |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in sorted(results, key=lambda row: (row.signal != "AL", row.symbol)):
        lines.append(
            f"| {item.symbol} | {item.signal} | {item.close:.2f} | "
            f"{item.buy_level:.2f} | {item.sell_level:.2f} | {item.stop_loss:.2f} | {item.note} |"
        )
    return "\n".join(lines) + "\n"
