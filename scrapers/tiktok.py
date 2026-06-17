from __future__ import annotations

import asyncio

from TikTokApi import TikTokApi

from base_scraper import BaseScraper
from config import ScraperConfig
from models import Platform, Post, ScrapeQuery, ScrapeResult


class TikTokScraper(BaseScraper):
    platform = Platform.TIKTOK

    def scrape(self, query: ScrapeQuery) -> ScrapeResult:
        result = self._empty_result(query)
        cfg = self.config.tiktok

        if not cfg.ms_token:
            result.errors.append(
                "TIKTOK_MS_TOKEN belum diset. Ambil dari cookie browser setelah buka tiktok.com"
            )
            return result

        try:
            posts, errors = asyncio.run(self._scrape_all(query))
            result.posts = self._dedupe_posts(posts)[: query.max_results]
            result.errors.extend(errors)
        except Exception as exc:
            result.errors.append(f"TikTok API error: {exc}")

        return result

    async def _scrape_all(self, query: ScrapeQuery) -> tuple[list[Post], list[str]]:
        cfg = self.config.tiktok
        posts: list[Post] = []
        errors: list[str] = []

        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[cfg.ms_token],
                num_sessions=1,
                sleep_after=3,
                browser=cfg.browser,
            )

            for hashtag in query.normalized_hashtags():
                try:
                    posts.extend(await self._scrape_hashtag(api, hashtag, query.max_results))
                except Exception as exc:
                    errors.append(f"Hashtag #{hashtag}: {exc}")
                self._delay()

            for keyword in query.normalized_keywords():
                try:
                    posts.extend(await self._scrape_keyword(api, keyword, query.max_results))
                except Exception as exc:
                    errors.append(f"Keyword '{keyword}': {exc}")
                self._delay()

            if query.location:
                try:
                    posts.extend(
                        await self._scrape_location(api, query.location, query.max_results)
                    )
                except Exception as exc:
                    errors.append(f"Lokasi '{query.location}': {exc}")

        return posts, errors

    async def _scrape_hashtag(
        self, api: TikTokApi, hashtag: str, max_results: int
    ) -> list[Post]:
        posts: list[Post] = []
        tag = api.hashtag(name=hashtag)

        async for video in tag.videos(count=max_results):
            posts.append(self._post_from_video(video.as_dict))

        return posts

    async def _scrape_keyword(
        self, api: TikTokApi, keyword: str, max_results: int
    ) -> list[Post]:
        posts: list[Post] = []

        async for video in api.search.videos(keyword, count=max_results):
            posts.append(self._post_from_video(video.as_dict))

        return posts

    async def _scrape_location(
        self, api: TikTokApi, location: str, max_results: int
    ) -> list[Post]:
        posts: list[Post] = []
        search_term = f"{location} place"
        count = 0

        async for video in api.search.videos(search_term, count=max_results * 2):
            data = video.as_dict
            poi_name = self._extract_poi_name(data)
            desc = (data.get("desc") or "").lower()

            if location.lower() in poi_name.lower() or location.lower() in desc:
                posts.append(
                    self._post_from_video(data, fallback_lokasi=poi_name or location)
                )
                count += 1
            if count >= max_results:
                break

        return posts

    def _extract_poi_name(self, data: dict) -> str:
        poi = data.get("poi") or {}
        if isinstance(poi, dict):
            return poi.get("name") or ""
        return ""

    def _post_from_video(self, data: dict, fallback_lokasi: str | None = None) -> Post:
        video_id = str(data.get("id", ""))
        author_info = data.get("author") or {}
        username = author_info.get("uniqueId", "unknown")
        stats = data.get("stats") or {}
        lokasi = fallback_lokasi or self._extract_poi_name(data)

        return Post(
            platform=Platform.TIKTOK,
            post_id=video_id,
            lokasi=lokasi,
            username=username,
            likes=int(stats.get("diggCount", 0)),
            comments=int(stats.get("commentCount", 0)),
            shares=int(stats.get("shareCount", 0)),
        )
