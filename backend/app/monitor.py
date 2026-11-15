import asyncio
import datetime as dt
import socket
import ssl
from urllib.parse import urlparse

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.database import SessionLocal, engine
from app.models import Business, WebsiteMonitor, Audit
from app.audit.engine import _ssl_info, _fetch
from app.security import validate_url

settings = get_settings()

scheduler = BackgroundScheduler()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def _check_single_site(business: Business, db) -> WebsiteMonitor:
    """Check a single website for uptime and SSL expiry."""
    website = business.website
    if not website:
        return None

    try:
        validate_url(website)
    except Exception:
        return None

    monitor = db.query(WebsiteMonitor).filter(WebsiteMonitor.business_id == business.id).first()
    if not monitor:
        monitor = WebsiteMonitor(business_id=business.id)
        db.add(monitor)
        db.commit()
        db.refresh(monitor)

    now = dt.datetime.utcnow()
    status = "up"
    response_ms = None
    site_down = False
    ssl_days = None
    ssl_expiring = False

    try:
        start = dt.datetime.utcnow()
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await _fetch(client, website)
        elapsed_ms = int((dt.datetime.utcnow() - start).total_seconds() * 1000)
        response_ms = elapsed_ms

        if resp is None or (resp.status_code and resp.status_code >= 500):
            status = "down"
            site_down = True
    except Exception:
        status = "down"
        site_down = True

    # SSL expiry check
    parsed = urlparse(website)
    if parsed.scheme == "https":
        try:
            host = parsed.hostname
            port = parsed.port or 443
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    if cert and "notAfter" in cert:
                        expiry = dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                        ssl_days = (expiry - now).days
                        if ssl_days <= settings.SSL_EXPIRY_WARNING_DAYS:
                            ssl_expiring = True
        except Exception:
            ssl_days = None

    monitor.last_check = now
    monitor.uptime_status = status
    monitor.response_time_ms = response_ms
    monitor.ssl_days_until_expiry = ssl_days
    monitor.ssl_expiring_soon = ssl_expiring
    monitor.site_down = site_down
    db.commit()
    db.refresh(monitor)
    return monitor


async def run_monitor_check():
    """Run monitoring check for all businesses with websites."""
    db = SessionLocal()
    try:
        businesses = db.query(Business).filter(Business.website.isnot(None)).all()
        for b in businesses:
            try:
                await _check_single_site(b, db)
            except Exception:
                continue
    finally:
        db.close()


def start_monitor():
    """Start the background scheduler."""
    if not scheduler.running:
        scheduler.add_job(
            lambda: asyncio.run(run_monitor_check()),
            trigger=IntervalTrigger(minutes=settings.MONITOR_INTERVAL_MINUTES),
            id="uptime_ssl_monitor",
            replace_existing=True,
        )
        scheduler.start()


def stop_monitor():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()


def get_monitor_dashboard(db):
    """Get dashboard summary of monitoring status."""
    monitors = db.query(WebsiteMonitor).all()
    sites_down = sum(1 for m in monitors if m.site_down)
    ssl_expiring = sum(1 for m in monitors if m.ssl_expiring_soon)
    return {"sites_down": sites_down, "ssl_expiring_soon": ssl_expiring, "total_monitored": len(monitors)}
