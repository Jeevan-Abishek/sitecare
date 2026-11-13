import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sitecare.db")
    # Crawl limits
    CRAWL_MAX_PAGES: int = int(os.getenv("CRAWL_MAX_PAGES", "10"))
    CRAWL_MAX_DEPTH: int = int(os.getenv("CRAWL_MAX_DEPTH", "2"))
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "15"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "4"))
    # Discovery
    OVERPASS_API_URL: str = os.getenv(
        "OVERPASS_API_URL", "https://overpass-api.de/api/interpreter"
    )
    OVERPASS_TIMEOUT: int = int(os.getenv("OVERPASS_TIMEOUT", "60"))
    # Scoring thresholds
    SLOW_RESPONSE_SECONDS: float = float(os.getenv("SLOW_RESPONSE_SECONDS", "3.0"))
    # AI
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "rules")  # rules | openai | anthropic
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
