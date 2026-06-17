#!/usr/bin/env python3
"""CLI entry point untuk hidden-gems-scraper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import ScraperConfig
from models import Platform, ScrapeQuery
from scrapers import InstagramScraper, ThreadsScraper, TikTokScraper
from utils import collect_csv_rows, save_results_csv, write_csv

SCRAPERS = {
    Platform.TIKTOK: TikTokScraper,
    Platform.INSTAGRAM: InstagramScraper,
    Platform.THREADS: ThreadsScraper,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape konten dari TikTok, Instagram, dan Threads "
        "berdasarkan hashtag, keyword, dan lokasi. Output: CSV."
    )
    parser.add_argument(
        "--platform",
        "-p",
        action="append",
        choices=[p.value for p in Platform],
        help="Platform target (bisa dipilih berkali-kali). Default: semua platform.",
    )
    parser.add_argument(
        "--hashtag",
        action="append",
        default=[],
        help="Hashtag tanpa # (bisa dipilih berkali-kali).",
    )
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="Keyword pencarian (bisa dipilih berkali-kali).",
    )
    parser.add_argument(
        "--location",
        "-l",
        default=None,
        help="Nama lokasi atau location ID (Instagram).",
    )
    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=50,
        help="Maksimum hasil per platform (default: 50).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path file CSV output. Default: output/scrape_<timestamp>.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.hashtag and not args.keyword and not args.location:
        print(
            "Error: minimal satu dari --hashtag, --keyword, atau --location harus diset.",
            file=sys.stderr,
        )
        return 1

    query = ScrapeQuery(
        hashtags=args.hashtag,
        keywords=args.keyword,
        location=args.location,
        max_results=args.max_results,
    )

    config = ScraperConfig.load()
    platforms = args.platform or [p.value for p in Platform]
    results = []

    for platform_name in platforms:
        platform = Platform(platform_name)
        scraper_cls = SCRAPERS[platform]
        scraper = scraper_cls(config)
        print(f"Scraping {platform.value}...", file=sys.stderr)

        result = scraper.scrape(query)
        results.append(result)

        if result.errors:
            for err in result.errors:
                print(f"  [{platform.value}] warning: {err}", file=sys.stderr)
        print(f"  -> {len(result.posts)} posts ditemukan", file=sys.stderr)

    rows = collect_csv_rows(results)

    if args.output:
        output_path = Path(args.output)
        write_csv(output_path, rows)
    else:
        output_path = save_results_csv(results, config.output_dir)

    print(f"Hasil disimpan ke: {output_path} ({len(rows)} baris)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
