import datetime as dt
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    Float,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True, index=True)
    phone = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    source_url = Column(String(1000), nullable=True)
    source = Column(String(50), nullable=True, default="manual")
    discovery_provider = Column(String(50), nullable=True, default="manual")  # osm | google_places | manual
    google_place_id = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=True, index=True)
    is_discovered = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    audits = relationship("Audit", back_populates="business", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="business", cascade="all, delete-orphan")
    monitors = relationship("WebsiteMonitor", back_populates="business", cascade="all, delete-orphan")


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    audit_date = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    http_status = Column(Integer, nullable=True)
    response_time = Column(String(50), nullable=True)
    ssl_status = Column(JSON, nullable=True)
    ssl_expiry_date = Column(DateTime, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    pagespeed_metrics = Column(JSON, nullable=True)
    core_web_vitals = Column(JSON, nullable=True)
    tech_stack = Column(JSON, nullable=True)
    verified_issues = Column(JSON, nullable=True)
    score = Column(Integer, nullable=True)
    audit_confidence = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)

    business = relationship("Business", back_populates="audits")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    priority = Column(String(50), nullable=True)  # high | medium | low
    lead_status = Column(String(50), nullable=True, default="new")  # new|contacted|interested|converted
    recommended_service = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    business = relationship("Business", back_populates="leads")


class WebsiteMonitor(Base):
    __tablename__ = "website_monitors"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    last_check = Column(DateTime, nullable=True)
    uptime_status = Column(String(50), nullable=True, default="unknown")  # up | down | unknown
    response_time_ms = Column(Float, nullable=True)
    ssl_days_until_expiry = Column(Integer, nullable=True)
    ssl_expiring_soon = Column(Boolean, default=False)
    site_down = Column(Boolean, default=False)
    alert_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    business = relationship("Business", back_populates="monitors")
