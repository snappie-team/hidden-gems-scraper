import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class InstagramConfig:
    username: str = os.getenv("INSTAGRAM_USERNAME", "")
    password: str = os.getenv("INSTAGRAM_PASSWORD", "")
    session_file: Path = BASE_DIR / ".sessions" / "instagram.session"


@dataclass
class TikTokConfig:
    ms_token: str = os.getenv("TIKTOK_MS_TOKEN", "")
    browser: str = os.getenv("TIKTOK_BROWSER", "chromium")


@dataclass
class ThreadsConfig:
    access_token: str = os.getenv("THREADS_ACCESS_TOKEN", "")
    user_id: str = os.getenv("THREADS_USER_ID", "")


@dataclass
class ScraperConfig:
    instagram: InstagramConfig
    tiktok: TikTokConfig
    threads: ThreadsConfig
    request_delay: float = float(os.getenv("REQUEST_DELAY", "1.5"))
    output_dir: Path = BASE_DIR / "output"

    @classmethod
    def load(cls) -> "ScraperConfig":
        return cls(
            instagram=InstagramConfig(),
            tiktok=TikTokConfig(),
            threads=ThreadsConfig(),
        )
