import datetime as dt
import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.security import validate_url, normalize_domain
from app.audit.scoring import compute_score, priority_for_score, service_for_flags
from app.config import get_settings

settings = get_settings()

PLACEHOLDER_EMAILS = {
    "info@example.com", "test@test.com", "name@domain.com",
    "youremail@email.com", "email@email.com", "admin@domain.com",
    "hello@example.com", "contact@example.com",
}
LOREM_MARKERS = {"lorem ipsum", "dolor sit amet", "consectetur", "placeholder text", "lorem"}


def _parse_url(website: str) -> str:
    return website if re.match(r"^https?://", website, re.IGNORECASE) else "https://" + website


async def _fetch(client: httpx.AsyncClient, url: str, timeout=None) -> httpx.Response | None:
    try:
        return await client.get(url, follow_redirects=True, timeout=timeout or settings.REQUEST_TIMEOUT)
    except Exception:
        return None


def _detect_redirect_issues(resp: httpx.Response) -> list[str]:
    issues = []
    if resp.history:
        for r in resp.history:
            if r.status_code in (301, 302, 307, 308):
                issues.append(f"Redirect {r.status_code} from {r.url} to {resp.url}")
    return issues


def _ssl_info(resp: httpx.Response, url: str) -> dict:
    info = {"https": False, "valid": None, "details": None}
    parsed = urlparse(url)
    info["https"] = parsed.scheme == "https"
    if not info["https"]:
        info["details"] = "Not using HTTPS"
        info["valid"] = False
        return info
    # httpx verifies certs by default using certifi. If we got here without
    # an SSLError, the cert verified OK.
    info["valid"] = True
    info["details"] = "SSL certificate verified"
    try:
        # Attempt to read peer certificate expiry info
        cert = resp.extensions.get("ssl_certificate") or resp.extensions.get("ssl_context")
    except Exception:
        cert = None
    return info


def _has_viewport(soup: BeautifulSoup) -> bool:
    for meta in soup.find_all("meta"):
        name = (meta.get("name") or "").lower()
        content = (meta.get("content") or "").lower()
        if name == "viewport" and content:
            return True
    return False


def _has_placeholder_email(text: str) -> bool:
    low = text.lower()
    return any(p in low for p in PLACEHOLDER_EMAILS)


def _has_lorem(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in LOREM_MARKERS)


def _old_copyright(text: str, now_year: int | None = None) -> bool:
    if now_year is None:
        now_year = dt.datetime.utcnow().year
    # Look for copyright years like 2015-2019 or single years
    years = re.findall(r"(?:©|copyright)\D*(\d{4})", text, re.IGNORECASE)
    years += re.findall(r"\b(19|20)\d{2}\b", text)
    for y in years:
        try:
            iy = int(y)
        except ValueError:
            continue
        if iy < now_year - 2:
            return True
    return False


async def audit_website(website: str, max_pages: int = 10, max_depth: int = 2) -> dict:
    """Run a full audit of a website. Returns a result dict."""
    url = _parse_url(website)
    validate_url(url)

    result: dict = {
        "website": url,
        "http_status": None,
        "reachable": False,
        "response_time": "0s",
        "response_time_seconds": 0.0,
        "ssl_status": {"https": False, "valid": None, "details": None},
        "performance_metrics": {},
        "verified_issues": [],
        "score": 0,
        "audit_confidence": "low",
        "details": {},
    }

    flags = {
        "unavailable": False,
        "invalid_ssl": False,
        "broken_internal_links": False,
        "missing_mobile_viewport": False,
        "slow_response": False,
        "placeholder_content": False,
        "missing_metadata": False,
        "missing_favicon": False,
        "broken_images": False,
        "broken_external_links": False,
        "old_copyright": False,
    }

    limits = httpx.Limits(max_connections=settings.MAX_CONCURRENT_REQUESTS)
    timeout = httpx.Timeout(settings.REQUEST_TIMEOUT)

    async with httpx.AsyncClient(limits=limits, timeout=timeout, follow_redirects=True) as client:
        start = dt.datetime.utcnow()
        resp = await _fetch(client, url)
        elapsed = (dt.datetime.utcnow() - start).total_seconds()

        if resp is None:
            flags["unavailable"] = True
            result["verified_issues"].append("Website is unreachable")
            result["audit_confidence"] = "high"
            result["score"] = compute_score(flags)
            result["priority"] = priority_for_score(result["score"])
            result["recommended_service"] = service_for_flags(flags, result["score"])
            result["details"] = {"crawled_pages": 0, "redirect_issues": []}
            return result

        result["http_status"] = resp.status_code
        result["reachable"] = True
        result["response_time_seconds"] = round(elapsed, 2)
        result["response_time"] = f"{round(elapsed, 2)}s"
        result["ssl_status"] = _ssl_info(resp, url)
        if not result["ssl_status"]["valid"]:
            flags["invalid_ssl"] = True
            result["verified_issues"].append("Invalid or missing SSL certificate")

        if elapsed >= settings.SLOW_RESPONSE_SECONDS:
            flags["slow_response"] = True
            result["verified_issues"].append(f"Slow response time ({result['response_time']})")

        redirect_issues = _detect_redirect_issues(resp)
        if redirect_issues:
            result["verified_issues"].extend(redirect_issues)

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # Performance metrics
        result["performance_metrics"] = {
            "html_size_bytes": len(html.encode("utf-8")),
            "response_time_seconds": round(elapsed, 2),
        }

        # Title / meta description
        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else None
        meta_desc = None
        for m in soup.find_all("meta"):
            if (m.get("name") or "").lower() == "description":
                meta_desc = m.get("content")
                break
        if not title_text and not meta_desc:
            flags["missing_metadata"] = True
            result["verified_issues"].append("Missing page title and meta description")
        elif not title_text:
            flags["missing_metadata"] = True
            result["verified_issues"].append("Missing page title")
        elif not meta_desc:
            flags["missing_metadata"] = True
            result["verified_issues"].append("Missing meta description")

        # Favicon
        favicon = None
        for link in soup.find_all("link"):
            rel = (link.get("rel") or [])
            if isinstance(rel, str):
                rel = [rel]
            if any("icon" in r.lower() for r in rel):
                favicon = link.get("href")
                break
        if not favicon:
            flags["missing_favicon"] = True
            result["verified_issues"].append("Missing favicon")

        # Mobile viewport
        if not _has_viewport(soup):
            flags["missing_mobile_viewport"] = True
            result["verified_issues"].append("Missing mobile viewport meta tag")

        # Content text analysis
        page_text = soup.get_text(" ", strip=True)
        if _has_placeholder_email(page_text):
            flags["placeholder_content"] = True
            result["verified_issues"].append("Placeholder email addresses detected")
        if _has_lorem(page_text):
            flags["placeholder_content"] = True
            result["verified_issues"].append("Lorem ipsum / placeholder content detected")
        if _old_copyright(page_text):
            flags["old_copyright"] = True
            result["verified_issues"].append("Outdated copyright date detected")

        # Images without alt
        images = soup.find_all("img")
        result["performance_metrics"]["image_count"] = len(images)
        images_no_alt = [img for img in images if not img.get("alt")]
        if images_no_alt:
            result["verified_issues"].append(f"{len(images_no_alt)} image(s) missing alt attribute")

        # Crawl internal links for broken links
        base_domain = normalize_domain(url)
        internal_links = set()
        external_links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            absolute = urljoin(url, href)
            parsed = urlparse(absolute)
            if parsed.scheme not in ("http", "https"):
                continue
            if normalize_domain(absolute) == base_domain:
                internal_links.add(absolute)
            else:
                external_links.add(absolute)

        # Crawl up to max_pages internal pages
        crawled = 0
        queue = list(internal_links)[: max_pages - 1]
        visited = {url}
        broken_internal = []
        while queue and crawled < max_pages - 1:
            next_url = queue.pop(0)
            if next_url in visited:
                continue
            visited.add(next_url)
            sub = await _fetch(client, next_url)
            crawled += 1
            if sub is None or sub.status_code >= 400:
                broken_internal.append(next_url)
                continue
            if len(queue) < max_pages - 1 - crawled:
                sub_soup = BeautifulSoup(sub.text, "html.parser")
                for a in sub_soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                        continue
                    abs2 = urljoin(next_url, href)
                    p2 = urlparse(abs2)
                    if p2.scheme not in ("http", "https"):
                        continue
                    if normalize_domain(abs2) == base_domain and abs2 not in visited and abs2 not in queue:
                        queue.append(abs2)

        if broken_internal:
            flags["broken_internal_links"] = True
            result["verified_issues"].append(f"{len(broken_internal)} broken internal link(s) detected")

        # Broken images
        broken_images = []
        for img in images[:20]:
            src = img.get("src")
            if not src:
                continue
            abs_src = urljoin(url, src)
            try:
                head = await client.head(abs_src, timeout=8, follow_redirects=True)
                if head.status_code >= 400:
                    broken_images.append(abs_src)
            except Exception:
                broken_images.append(abs_src)
        if broken_images:
            flags["broken_images"] = True
            result["verified_issues"].append(f"{len(broken_images)} broken image(s) detected")

        # External links sample check (limited)
        broken_external = []
        for ext in list(external_links)[:5]:
            try:
                head = await client.head(ext, timeout=8, follow_redirects=True)
                if head.status_code >= 400:
                    broken_external.append(ext)
            except Exception:
                pass
        if broken_external:
            flags["broken_external_links"] = True
            result["verified_issues"].append(f"{len(broken_external)} broken external link(s) detected")

        result["details"] = {
            "crawled_pages": crawled + 1,
            "internal_links_found": len(internal_links),
            "external_links_found": len(external_links),
            "redirect_issues": redirect_issues,
            "title": title_text,
            "meta_description": meta_desc,
        }

    result["verified_issues"] = list(dict.fromkeys(result["verified_issues"]))
    result["score"] = compute_score(flags)
    result["priority"] = priority_for_score(result["score"])
    result["recommended_service"] = service_for_flags(flags, result["score"])

    # Confidence: high if reachable and checks ran; medium if partial
    if result["reachable"]:
        result["audit_confidence"] = "high" if crawled + 1 >= 2 else "medium"
    else:
        result["audit_confidence"] = "high"

    return result
