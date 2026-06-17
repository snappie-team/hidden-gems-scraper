"""Utility helpers untuk scraper."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from models import CSV_COLUMNS, ScrapeResult


def save_results_csv(results: list[ScrapeResult], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    platforms = "_".join(sorted({r.platform.value for r in results}))
    filepath = output_dir / f"scrape_{platforms}_{timestamp}.csv"

    rows = collect_csv_rows(results)
    write_csv(filepath, rows)
    return filepath


def collect_csv_rows(results: list[ScrapeResult]) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    seen: set[tuple[str, str]] = set()

    for result in results:
        for post in result.posts:
            key = (post.platform.value, post.post_id)
            if key in seen:
                continue
            seen.add(key)
            rows.append(post.to_csv_row())

    return rows


def write_csv(filepath: Path, rows: list[dict[str, str | int]]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
