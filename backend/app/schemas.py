from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, HttpUrl, Field, validator


class BusinessBase(BaseModel):
    business_name: str
    category: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    source_url: Optional[str] = None
    source: Optional[str] = "manual"


class BusinessCreate(BusinessBase):
    pass


class BusinessOut(BusinessBase):
    id: int
    domain: Optional[str] = None
    is_discovered: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuditBase(BaseModel):
    http_status: Optional[int] = None
    response_time: Optional[str] = None
    ssl_status: Optional[dict] = None
    performance_metrics: Optional[dict] = None
    verified_issues: Optional[list] = None
    score: Optional[int] = None
    audit_confidence: Optional[str] = None
    details: Optional[dict] = None


class AuditCreate(AuditBase):
    business_id: int


class AuditOut(AuditBase):
    id: int
    business_id: int
    audit_date: datetime

    class Config:
        from_attributes = True


class LeadBase(BaseModel):
    priority: Optional[str] = None
    lead_status: Optional[str] = "new"
    recommended_service: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    business_id: Optional[int] = None


class LeadOut(LeadBase):
    id: int
    business_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LeadWithBusiness(LeadOut):
    business: BusinessOut

    class Config:
        from_attributes = True


# Discovery
class DiscoveryFilters(BaseModel):
    country: str = "India"
    state: str = "Tamil Nadu"
    city: Optional[str] = None
    category: str = "All businesses"
    industry: Optional[str] = None
    website_available: bool = True
    limit: int = Field(default=50, ge=1, le=500)


class DiscoveredBusiness(BaseModel):
    business_name: str
    category: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    source_url: Optional[str] = None


class DiscoveryResult(BaseModel):
    total: int
    businesses: List[DiscoveredBusiness]
    provider: str
    coverage_note: str
    filters: DiscoveryFilters


# Audit
class AuditRequest(BaseModel):
    website: str
    business_id: Optional[int] = None
    max_pages: Optional[int] = None


class AuditResult(BaseModel):
    business_id: Optional[int] = None
    website: str
    http_status: Optional[int]
    reachable: bool
    response_time: str
    ssl_status: dict
    performance_metrics: dict
    verified_issues: list
    score: int
    audit_confidence: str
    details: dict


class BulkAuditRequest(BaseModel):
    website_urls: List[str]
    max_pages: Optional[int] = None


# Scoring
class ScoreBreakdown(BaseModel):
    issue: str
    points: int


# Lead management
class LeadStatusUpdate(BaseModel):
    lead_status: str
    notes: Optional[str] = None


class LeadPriorityUpdate(BaseModel):
    priority: str


# Outreach
class OutreachGenerate(BaseModel):
    business_id: int
    include_whatsapp: bool = True
    include_email: bool = True
    include_proposal: bool = True
    include_followup: bool = True


class OutreachResult(BaseModel):
    business_id: int
    whatsapp_message: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    proposal: Optional[str] = None
    followup_message: Optional[str] = None
    audit_summary: Optional[str] = None


# Report
class ReportGenerate(BaseModel):
    business_id: int
    provider: Optional[str] = "rules"


class ReportOut(BaseModel):
    business_id: int
    report_title: str
    report_body: str
    generated_at: datetime
    provider: str


# CSV import
class CsvImportResult(BaseModel):
    imported: int
    skipped: int
    errors: List[str] = []


# Stats
class DashboardStats(BaseModel):
    total_businesses: int
    websites_found: int
    websites_audited: int
    websites_with_issues: int
    high_priority_leads: int
    potential_monthly_revenue: int


# Generic message
class Message(BaseModel):
    message: str
