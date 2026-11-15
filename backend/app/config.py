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
    # Google APIs (optional, free tier)
    GOOGLE_PLACES_API_KEY: str | None = os.getenv("GOOGLE_PLACES_API_KEY")
    GOOGLE_PAGESPEED_API_KEY: str | None = os.getenv("GOOGLE_PAGESPEED_API_KEY")
    # Monitoring
    MONITOR_INTERVAL_MINUTES: int = int(os.getenv("MONITOR_INTERVAL_MINUTES", "1440"))
    SSL_EXPIRY_WARNING_DAYS: int = int(os.getenv("SSL_EXPIRY_WARNING_DAYS", "30"))
    # Branding
    AGENCY_NAME: str = os.getenv("AGENCY_NAME", "SiteCare AI")
    AGENCY_TAGLINE: str = os.getenv("AGENCY_TAGLINE", "Website Maintenance & Lead Generation")
    AGENCY_EMAIL: str = os.getenv("AGENCY_EMAIL", "hello@sitecare.ai")
    AGENCY_PHONE: str = os.getenv("AGENCY_PHONE", "")
    AGENCY_WEBSITE: str = os.getenv("AGENCY_WEBSITE", "https://sitecare.ai")
    # SMTP (optional, for direct email sending)
    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str | None = os.getenv("SMTP_USER")
    SMTP_PASS: str | None = os.getenv("SMTP_PASS")
    SMTP_FROM: str | None = os.getenv("SMTP_FROM")


@lru_cache
def get_settings() -> Settings:
    return Settings()
