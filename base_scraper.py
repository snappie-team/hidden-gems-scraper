from abc import ABC, abstractmethod
import time

from config import ScraperConfig
from models import Platform, Post, ScrapeQuery, ScrapeResult


class BaseScraper(ABC):
    platform: Platform

    def __init__(self, config: ScraperConfig):
        self.config = config

    @abstractmethod
    def scrape(self, query: ScrapeQuery) -> ScrapeResult:
        """Jalankan scraping berdasarkan hashtag, keyword, dan/atau lokasi."""

    def _empty_result(self, query: ScrapeQuery) -> ScrapeResult:
        return ScrapeResult(platform=self.platform, query=query)

    def _dedupe_posts(self, posts: list[Post]) -> list[Post]:
        seen: set[str] = set()
        unique: list[Post] = []
        for post in posts:
            if post.post_id not in seen:
                seen.add(post.post_id)
                unique.append(post)
        return unique

    def _delay(self) -> None:
        time.sleep(self.config.request_delay)
