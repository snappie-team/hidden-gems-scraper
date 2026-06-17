from __future__ import annotations

import httpx

from base_scraper import BaseScraper
from config import ScraperConfig
from models import Platform, Post, ScrapeQuery, ScrapeResult

GRAPH_API_BASE = "https://graph.threads.net/v1.0"


class ThreadsScraper(BaseScraper):
    platform = Platform.THREADS

    def scrape(self, query: ScrapeQuery) -> ScrapeResult:
        result = self._empty_result(query)
        token = self.config.threads.access_token

        if not token:
            result.errors.append(
                "THREADS_ACCESS_TOKEN belum diset. "
                "Dapatkan dari Meta Developer (Threads API)."
            )
            return result

        posts: list[Post] = []

        for hashtag in query.normalized_hashtags():
            try:
                posts.extend(self._search_hashtag(token, hashtag, query.max_results))
            except Exception as exc:
                result.errors.append(f"Hashtag #{hashtag}: {exc}")
            self._delay()

        for keyword in query.normalized_keywords():
            try:
                posts.extend(self._search_keyword(token, keyword, query.max_results))
            except Exception as exc:
                result.errors.append(f"Keyword '{keyword}': {exc}")
            self._delay()

        if query.location:
            try:
                posts.extend(
                    self._search_location(token, query.location, query.max_results)
                )
            except Exception as exc:
                result.errors.append(f"Lokasi '{query.location}': {exc}")

        result.posts = self._dedupe_posts(posts)[: query.max_results]
        return result

    def _headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def _search_hashtag(self, token: str, hashtag: str, max_results: int) -> list[Post]:
        return self._keyword_search(token, f"#{hashtag}", max_results)

    def _search_keyword(self, token: str, keyword: str, max_results: int) -> list[Post]:
        return self._keyword_search(token, keyword, max_results)

    def _search_location(self, token: str, location: str, max_results: int) -> list[Post]:
        return self._keyword_search(token, location, max_results, fallback_lokasi=location)

    def _keyword_search(
        self,
        token: str,
        query_text: str,
        max_results: int,
        fallback_lokasi: str = "",
    ) -> list[Post]:
        posts: list[Post] = []
        user_id = self.config.threads.user_id

        params: dict[str, str | int] = {
            "q": query_text,
            "search_type": "RECENT",
            "limit": min(max_results, 50),
        }
        if user_id:
            params["user_id"] = user_id

        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{GRAPH_API_BASE}/keyword_search",
                headers=self._headers(token),
                params=params,
            )
            response.raise_for_status()
            data = response.json()

        for item in data.get("data", []):
            posts.append(self._post_from_item(item, fallback_lokasi=fallback_lokasi))

        return posts

    def _post_from_item(self, item: dict, fallback_lokasi: str = "") -> Post:
        post_id = str(item.get("id", ""))
        username = item.get("username") or item.get("owner", {}).get("username", "unknown")

        location_data = item.get("location") or {}
        lokasi = fallback_lokasi
        if not lokasi and isinstance(location_data, dict):
            lokasi = location_data.get("name") or ""

        return Post(
            platform=Platform.THREADS,
            post_id=post_id,
            lokasi=lokasi,
            username=username,
            likes=int(item.get("like_count", 0)),
            comments=int(item.get("reply_count", 0)),
            shares=int(item.get("repost_count", 0)),
        )
