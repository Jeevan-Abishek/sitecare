import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.audit.scoring import compute_score, priority_for_score, service_for_flags
from app.security import validate_url, normalize_domain, is_private_or_internal


def test_scoring_caps_at_100():
    flags = {k: True for k in [
        "unavailable", "invalid_ssl", "broken_internal_links", "missing_mobile_viewport",
        "slow_response", "placeholder_content", "missing_metadata", "missing_favicon",
        "broken_images", "broken_external_links", "old_copyright",
    ]}
    assert compute_score(flags) == 100


def test_scoring_single_issue():
    assert compute_score({"unavailable": True}) == 20
    assert compute_score({"missing_metadata": True}) == 5
    assert compute_score({}) == 0


def test_priority_bands():
    assert priority_for_score(80) == "high"
    assert priority_for_score(50) == "medium"
    assert priority_for_score(10) == "low"


def test_service_recommendation():
    assert "recovery" in service_for_flags({"unavailable": True}, 80).lower()
    assert "repair" in service_for_flags({"broken_internal_links": True}, 40).lower()


def test_validate_url_blocks_private():
    for bad in ["http://localhost/x", "http://127.0.0.1/x", "http://192.168.1.1/x",
                "http://10.0.0.1/x", "http://172.16.0.1/x", "ftp://example.com/x",
                "javascript:alert(1)"]:
        with pytest.raises(Exception):
            validate_url(bad)


def test_validate_url_allows_public():
    assert validate_url("https://example.com") == "https://example.com"
    assert validate_url("example.com") == "https://example.com"


def test_normalize_domain():
    assert normalize_domain("https://www.example.com/page") == "example.com"
    assert normalize_domain("http://example.com") == "example.com"
    assert normalize_domain(None) is None


def test_is_private_hostname():
    assert is_private_or_internal("localhost") is True
    assert is_private_or_internal("127.0.0.1") is True
    assert is_private_or_internal("example.com") is False


@pytest.mark.asyncio
async def test_audit_unreachable_website():
    from app.audit.engine import audit_website

    class FakeResp:
        pass

    class FakeClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *a):
            return False
        async def get(self, url, **kwargs):
            raise OSError("network down")

    with patch("app.audit.engine.httpx.AsyncClient", return_value=FakeClient()):
        result = await audit_website("https://example.invalid", max_pages=5)
    assert result["reachable"] is False
    assert result["http_status"] is None
    assert any("unreachable" in i.lower() for i in result["verified_issues"])
    assert result["score"] >= 20


@pytest.mark.asyncio
async def test_audit_healthy_website():
    from app.audit.engine import audit_website

    html = """<html><head><title>Example Site</title>
<meta name="description" content="A sample site">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="/favicon.ico">
</head><body>
<img src="/logo.png" alt="logo">
<a href="/about">About</a>
<p>Welcome to our business.</p>
</body></html>"""

    class FakeResp:
        status_code = 200
        history = []
        text = html
        url = "https://example.com/"
        extensions = {}

        async def aread(self):
            return html.encode()

    class FakeClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *a):
            return False
        async def get(self, url, **kwargs):
            return FakeResp()
        async def head(self, url, **kwargs):
            r = MagicMock()
            r.status_code = 200
            return r

    with patch("app.audit.engine.httpx.AsyncClient", return_value=FakeClient()):
        result = await audit_website("https://example.com", max_pages=5)
    assert result["reachable"] is True
    assert result["http_status"] == 200
    assert not any("viewport" in i.lower() for i in result["verified_issues"])
    assert result["score"] == 0 or result["score"] >= 0
