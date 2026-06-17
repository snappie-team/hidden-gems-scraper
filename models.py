from dataclasses import dataclass, field, asdict
from enum import Enum

CSV_COLUMNS = ["platform", "lokasi", "username", "likes", "comments", "shares"]


class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    THREADS = "threads"


@dataclass
class ScrapeQuery:
    hashtags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    location: str | None = None
    max_results: int = 50

    def normalized_hashtags(self) -> list[str]:
        return [tag.lstrip("#").lower() for tag in self.hashtags if tag.strip()]

    def normalized_keywords(self) -> list[str]:
        return [kw.strip() for kw in self.keywords if kw.strip()]


@dataclass
class Post:
    platform: Platform
    post_id: str
    lokasi: str = ""
    username: str = ""
    likes: int = 0
    comments: int = 0
    shares: int = 0

    def to_csv_row(self) -> dict[str, str | int]:
        return {
            "platform": self.platform.value,
            "lokasi": self.lokasi,
            "username": self.username,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
        }


@dataclass
class ScrapeResult:
    platform: Platform
    query: ScrapeQuery
    posts: list[Post] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

