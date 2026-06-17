from __future__ import annotations

import instaloader

from base_scraper import BaseScraper
from config import ScraperConfig
from models import Platform, Post, ScrapeQuery, ScrapeResult


class InstagramScraper(BaseScraper):
    platform = Platform.INSTAGRAM

    def __init__(self, config: ScraperConfig):
        super().__init__(config)
        self._loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )
        self._logged_in = False

    def scrape(self, query: ScrapeQuery) -> ScrapeResult:
        result = self._empty_result(query)
        try:
            self._ensure_login()
        except Exception as exc:
            result.errors.append(f"Login gagal: {exc}")
            return result

        posts: list[Post] = []

        for hashtag in query.normalized_hashtags():
            try:
                posts.extend(self._scrape_hashtag(hashtag, query.max_results))
            except Exception as exc:
                result.errors.append(f"Hashtag #{hashtag}: {exc}")
            self._delay()

        for keyword in query.normalized_keywords():
            try:
                posts.extend(self._scrape_keyword(keyword, query.max_results))
            except Exception as exc:
                result.errors.append(f"Keyword '{keyword}': {exc}")
            self._delay()

        if query.location:
            try:
                posts.extend(self._scrape_location(query.location, query.max_results))
            except Exception as exc:
                result.errors.append(f"Lokasi '{query.location}': {exc}")

        result.posts = self._dedupe_posts(posts)[: query.max_results]
        return result

    def _ensure_login(self) -> None:
        if self._logged_in:
            return

        cfg = self.config.instagram
        session_path = cfg.session_file
        session_path.parent.mkdir(parents=True, exist_ok=True)

        if session_path.exists():
            self._loader.load_session_from_file(cfg.username, session_path)
            self._logged_in = True
            return

        if not cfg.username or not cfg.password:
            raise ValueError(
                "Set INSTAGRAM_USERNAME dan INSTAGRAM_PASSWORD di .env, "
                "atau simpan session di .sessions/instagram.session"
            )

        self._loader.login(cfg.username, cfg.password)
        self._loader.save_session_to_file(session_path)
        self._logged_in = True

    def _scrape_hashtag(self, hashtag: str, max_results: int) -> list[Post]:
        posts: list[Post] = []
        hashtag_obj = instaloader.Hashtag.from_name(self._loader.context, hashtag)

        for idx, node in enumerate(hashtag_obj.get_posts()):
            if idx >= max_results:
                break
            posts.append(self._post_from_node(node))

        return posts

    def _scrape_keyword(self, keyword: str, max_results: int) -> list[Post]:
        posts: list[Post] = []
        search_tag = keyword.replace(" ", "").lower()

        try:
            hashtag_obj = instaloader.Hashtag.from_name(self._loader.context, search_tag)
            for idx, node in enumerate(hashtag_obj.get_posts()):
                if idx >= max_results * 3:
                    break
                caption = node.caption or ""
                if keyword.lower() in caption.lower():
                    posts.append(self._post_from_node(node))
                if len(posts) >= max_results:
                    break
        except instaloader.exceptions.QueryReturnedNotFoundException:
            pass

        return posts

    def _scrape_location(self, location: str, max_results: int) -> list[Post]:
        posts: list[Post] = []
        location_id = self._resolve_location_id(location)
        loc = instaloader.Location.from_id(self._loader.context, location_id)
        place_name = loc.name

        for idx, node in enumerate(loc.get_posts()):
            if idx >= max_results:
                break
            posts.append(self._post_from_node(node, fallback_lokasi=place_name))

        return posts

    def _resolve_location_id(self, location: str) -> int:
        if location.isdigit():
            return int(location)

        results = instaloader.TopSearchResults(self._loader.context, location)
        for place in results.get_locations():
            return place.id

        raise ValueError(f"Lokasi '{location}' tidak ditemukan")

    def _post_from_node(self, node, fallback_lokasi: str | None = None) -> Post:
        lokasi = fallback_lokasi or ""
        if not lokasi and node.location:
            lokasi = node.location.name

        return Post(
            platform=Platform.INSTAGRAM,
            post_id=node.shortcode,
            lokasi=lokasi,
            username=node.owner_username,
            likes=node.likes,
            comments=node.comments,
            shares=0,
        )
