import csv
import io
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db, init_db
from app.deps import rate_limit
from app.config import get_settings
from app.security import validate_url, normalize_domain
from app.discovery import get_discovery_provider
from app.audit import audit_website
from app.reports.generator import generate_report
from app.reports import generate_pdf_report
from app.outreach import generate_outreach
from app.audit.scoring import priority_for_score, service_for_flags

import app.models as models
import app.schemas as schemas
import app.crud as crud

router = APIRouter()
settings = get_settings()


@router.on_event("startup")
def _startup():
    init_db()


# ---------- Discovery ----------

@router.post("/discover", response_model=schemas.DiscoveryResult)
async def discover(filters: schemas.DiscoveryFilters, db: Session = Depends(get_db)):
    provider = get_discovery_provider(filters.provider or "osm")
    try:
        result = await provider.discover(filters)
    except RuntimeError as exc:
        # Free discovery source unavailable: surface a clear error and point
        # users to the working offline alternatives (CSV import / manual add).
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Discovery provider unavailable",
                "message": str(exc),
                "fallback": "Use CSV import (POST /api/import/csv) or add websites manually (POST /api/audit).",
            },
        )
    for b in result.businesses:
        crud.create_business(db, b)
    return result


# ---------- Audit ----------

@router.post("/audit", response_model=schemas.AuditResult)
async def audit(req: schemas.AuditRequest, db: Session = Depends(get_db)):
    url = req.website if "://" in req.website else "https://" + req.website
    validate_url(url)
    max_pages = req.max_pages or settings.CRAWL_MAX_PAGES
    result = await audit_website(url, max_pages=max_pages)

    business = None
    domain = normalize_domain(result["website"])
    if domain:
        business = crud.get_business_by_domain(db, domain)
    if req.business_id:
        business = crud.get_business(db, req.business_id)

    if not business:
        from urllib.parse import urlparse
        parsed = urlparse(result["website"])
        business = crud.create_business(db, schemas.BusinessCreate(
            business_name=parsed.hostname or "Audited Website",
            category="Manual",
            website=result["website"],
            source="manual",
        ))

    crud.create_audit(db, business.id, result)
    result["business_id"] = business.id

    existing_lead = next(iter(business.leads), None)
    if not existing_lead:
        flags = {i.split(" ")[0].lower(): True for i in result.get("verified_issues", [])}
        crud.create_lead(db, business.id, schemas.LeadCreate(
            priority=priority_for_score(result["score"]),
            recommended_service=service_for_flags(flags, result["score"]),
        ))

    return result


@router.post("/audit/bulk", response_model=list[schemas.AuditResult])
async def audit_bulk(req: schemas.BulkAuditRequest, db: Session = Depends(get_db)):
    results = []
    for url in req.website_urls:
        u = url if "://" in url else "https://" + url
        validate_url(u)
        max_pages = req.max_pages or settings.CRAWL_MAX_PAGES
        result = await audit_website(u, max_pages=max_pages)
        results.append(result)
    return results


# ---------- Businesses ----------

@router.get("/businesses", response_model=list[schemas.BusinessOut])
def list_businesses(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_businesses(db, skip=skip, limit=limit, search=search, category=category, city=city)


@router.post("/businesses", response_model=schemas.BusinessOut)
def create_business_endpoint(business_in: schemas.BusinessCreate, db: Session = Depends(get_db)):
    return crud.create_business(db, business_in)


@router.post("/import/csv", response_model=schemas.CsvImportResult)
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="A CSV file is required")
    content = file.file.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    imported = 0
    skipped = 0
    errors = []
    for row_num, row in enumerate(reader, start=2):
        try:
            b = schemas.BusinessCreate(
                business_name=(row.get("business_name") or row.get("name") or "").strip() or f"Business {row_num}",
                category=(row.get("category") or "Manual").strip(),
                city=(row.get("city") or "").strip() or None,
                state=(row.get("state") or "").strip() or None,
                country=(row.get("country") or "India").strip() or None,
                website=(row.get("website") or "").strip() or None,
                phone=(row.get("phone") or "").strip() or None,
                email=(row.get("email") or "").strip() or None,
                address=(row.get("address") or "").strip() or None,
                source_url=(row.get("source_url") or "").strip() or None,
                source="csv",
            )
            crud.create_business(db, b)
            imported += 1
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            errors.append(f"Row {row_num}: {exc}")
    return schemas.CsvImportResult(imported=imported, skipped=skipped, errors=errors[:50])


# ---------- Leads ----------

@router.get("/leads", response_model=list[schemas.LeadWithBusiness])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_leads(db, skip=skip, limit=limit, search=search, category=category, city=city,
                          priority=priority, status=status)


@router.get("/leads/{lead_id}", response_model=schemas.LeadWithBusiness)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = crud.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/leads/{lead_id}", response_model=schemas.LeadWithBusiness)
def patch_lead(lead_id: int, lead_in: schemas.LeadStatusUpdate, db: Session = Depends(get_db)):
    lead = crud.update_lead(db, lead_id, lead_in)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_lead(db, lead_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead not found")
    return None


# ---------- Reports ----------

@router.get("/reports", response_model=list[schemas.ReportOut])
def list_reports(db: Session = Depends(get_db)):
    audits = (
        db.query(models.Audit)
        .join(models.Business)
        .order_by(models.Audit.audit_date.desc())
        .all()
    )
    return [generate_report(a.business, a, provider="rules") for a in audits]


@router.get("/reports/{business_id}", response_model=schemas.ReportOut)
def get_report(business_id: int, provider: Optional[str] = "rules", db: Session = Depends(get_db)):
    business = crud.get_business(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    audits = crud.get_audits_for_business(db, business_id)
    audit = audits[0] if audits else None
    return generate_report(business, audit, provider=provider or "rules")


@router.get("/reports/{business_id}/pdf")
def download_pdf_report(business_id: int, db: Session = Depends(get_db)):
    from fastapi.responses import Response
    business = crud.get_business(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    audits = crud.get_audits_for_business(db, business_id)
    audit = audits[0] if audits else None
    pdf_bytes = generate_pdf_report(business, audit)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=sitecare_audit_{business_id}.pdf"},
    )


# ---------- CSV export ----------

@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    leads = crud.get_leads(db, skip=0, limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Business Name", "City", "Category", "Website", "Score",
        "Issues", "Phone", "Email", "Status", "Priority",
    ])
    for lead in leads:
        b = lead.business
        audit = None
        if b.audits:
            audit = sorted(b.audits, key=lambda a: a.audit_date or a.id, reverse=True)[0]
        issues = audit.verified_issues if audit and audit.verified_issues else []
        writer.writerow([
            b.business_name, b.city or "", b.category, b.website or "",
            audit.score if audit else "", len(issues) if issues else 0,
            b.phone or "", b.email or "", lead.lead_status or "new",
            lead.priority or "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sitecare_leads.csv"},
    )


# ---------- Outreach ----------

@router.post("/outreach/generate", response_model=schemas.OutreachResult)
def outreach_generate(req: schemas.OutreachGenerate, db: Session = Depends(get_db)):
    business = crud.get_business(db, req.business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    audits = crud.get_audits_for_business(db, req.business_id)
    audit = audits[0] if audits else None
    return generate_outreach(business, audit, req)


# ---------- Uptime & SSL Monitor ----------

@router.post("/monitor/check")
def run_monitor_check_endpoint(db: Session = Depends(get_db)):
    import asyncio
    from app.monitor import run_monitor_check
    asyncio.run(run_monitor_check())
    return {"message": "Monitor check completed for all tracked websites"}


@router.get("/monitor/status", response_model=list[schemas.MonitorOut])
def monitor_status(db: Session = Depends(get_db)):
    from app.monitor import get_monitor_dashboard
    monitors = db.query(models.WebsiteMonitor).all()
    return monitors


@router.get("/monitor/dashboard")
def monitor_dashboard(db: Session = Depends(get_db)):
    from app.monitor import get_monitor_dashboard
    return get_monitor_dashboard(db)
