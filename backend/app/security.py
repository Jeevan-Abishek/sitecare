import ipaddress
import re
from typing import Optional
from urllib.parse import urlparse

from fastapi import HTTPException

BLOCKED_MESSAGE = "URL not allowed for crawling"


def is_private_or_internal(hostname: str) -> bool:
    """Return True if hostname resolves to a private/internal address."""
    try:
        info = ipaddress.ip_address(hostname)
        return (
            info.is_private
            or info.is_loopback
            or info.is_link_local
            or info.is_multicast
            or info.is_reserved
            or info.is_unspecified
        )
    except ValueError:
        pass
    # Hostname may be a domain; resolve via socket would require network.
    # Block common internal hostnames explicitly.
    internal_suffixes = (".local", ".localhost", ".internal", ".intranet")
    lower = hostname.lower()
    if lower in ("localhost", "local") or lower.endswith(internal_suffixes):
        return True
    return False


def validate_url(url: str) -> str:
    """Validate and sanitize a URL. Blocks non-http(s) and internal addresses."""
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=400, detail="URL is required")
    url = url.strip()
    scheme_match = re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*):", url)
    if scheme_match and scheme_match.group(1).lower() not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http:// and https:// URLs are allowed")
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url
    parsed_check = urlparse(url)
    if parsed_check.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http:// and https:// URLs are allowed")
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL")
    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL: missing host")
    if is_private_or_internal(parsed.hostname):
        raise HTTPException(status_code=400, detail=BLOCKED_MESSAGE)
    # Block common private IP ranges explicitly by string prefix as a fallback
    host = parsed.hostname.lower()
    private_prefixes = (
        "10.",
        "172.16.",
        "172.17.",
        "172.18.",
        "172.19.",
        "172.20.",
        "172.21.",
        "172.22.",
        "172.23.",
        "172.24.",
        "172.25.",
        "172.26.",
        "172.27.",
        "172.28.",
        "172.29.",
        "172.30.",
        "172.31.",
        "192.168.",
        "169.254.",
        "127.",
        "0.0.0.0",
    )
    if host.startswith(private_prefixes):
        raise HTTPException(status_code=400, detail=BLOCKED_MESSAGE)
    return url


def normalize_domain(website: Optional[str]) -> Optional[str]:
    if not website:
        return None
    try:
        parsed = urlparse(website if "://" in website else "https://" + website)
    except Exception:
        return None
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None
