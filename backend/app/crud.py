from typing import Optional

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, or_

import app.models as models
import app.schemas as schemas
from app.security import normalize_domain


def get_business(db: Session, business_id: int) -> Optional[models.Business]:
    return db.query(models.Business).filter(models.Business.id == business_id).first()


def get_business_by_domain(db: Session, domain: str) -> Optional[models.Business]:
    return db.query(models.Business).filter(models.Business.domain == domain).first()


def get_businesses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
):
    q = db.query(models.Business)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            models.Business.business_name.ilike(like),
            models.Business.city.ilike(like),
            models.Business.category.ilike(like),
        ))
    if category:
        q = q.filter(models.Business.category == category)
    if city:
        q = q.filter(models.Business.city == city)
    q = q.offset(skip).limit(limit)
    return q.all()


def count_businesses(db: Session) -> int:
    return db.query(func.count(models.Business.id)).scalar() or 0


def count_websites_found(db: Session) -> int:
    return db.query(func.count(models.Business.id)).filter(models.Business.website.isnot(None)).scalar() or 0


def count_websites_audited(db: Session) -> int:
    return db.query(func.count(models.Audit.id)).scalar() or 0


def count_websites_with_issues(db: Session) -> int:
    return (
        db.query(func.count(models.Business.id))
        .join(models.Audit, models.Audit.business_id == models.Business.id)
        .filter(models.Audit.score > 0)
        .distinct()
        .scalar()
        or 0
    )


def count_high_priority_leads(db: Session) -> int:
    return (
        db.query(func.count(models.Lead.id))
        .filter(models.Lead.priority == "high")
        .scalar()
        or 0
    )


def potential_monthly_revenue(db: Session) -> int:
    high = count_high_priority_leads(db)
    return high * 500  # estimated ₹/month per lead


def create_business(db: Session, business_in: schemas.BusinessCreate) -> models.Business:
    domain = normalize_domain(business_in.website)
    existing = None
    if domain:
        existing = get_business_by_domain(db, domain)
    if existing:
        return existing
    db_obj = models.Business(**business_in.model_dump(), domain=domain)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_businesses(db: Session, businesses: list[schemas.BusinessCreate]):
    created = 0
    skipped = 0
    errors = []
    for b in businesses:
        try:
            obj = create_business(db, b)
            if obj:
                created += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            skipped += 1
    return created, skipped, errors


def get_audit(db: Session, audit_id: int) -> Optional[models.Audit]:
    return db.query(models.Audit).filter(models.Audit.id == audit_id).first()


def create_audit(db: Session, business_id: int, audit_result: dict) -> models.Audit:
    db_obj = models.Audit(
        business_id=business_id,
        http_status=audit_result.get("http_status"),
        response_time=audit_result.get("response_time"),
        ssl_status=audit_result.get("ssl_status"),
        performance_metrics=audit_result.get("performance_metrics"),
        verified_issues=audit_result.get("verified_issues"),
        score=audit_result.get("score"),
        audit_confidence=audit_result.get("audit_confidence"),
        details=audit_result.get("details"),
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_audits_for_business(db: Session, business_id: int):
    return (
        db.query(models.Audit)
        .filter(models.Audit.business_id == business_id)
        .order_by(models.Audit.audit_date.desc())
        .all()
    )


def get_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
):
    q = db.query(models.Lead).join(models.Business, models.Lead.business_id == models.Business.id)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            models.Business.business_name.ilike(like),
            models.Business.city.ilike(like),
        ))
    if category:
        q = q.filter(models.Business.category == category)
    if city:
        q = q.filter(models.Business.city == city)
    if priority:
        q = q.filter(models.Lead.priority == priority)
    if status:
        q = q.filter(models.Lead.lead_status == status)
    q = q.options(selectinload(models.Lead.business)).offset(skip).limit(limit)
    return q.all()


def get_lead(db: Session, lead_id: int) -> Optional[models.Lead]:
    return (
        db.query(models.Lead)
        .options(selectinload(models.Lead.business))
        .filter(models.Lead.id == lead_id)
        .first()
    )


def create_lead(db: Session, business_id: int, lead_in: schemas.LeadCreate) -> models.Lead:
    db_obj = models.Lead(business_id=business_id, **lead_in.model_dump(exclude={"business_id"}))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_lead(db: Session, lead_id: int, lead_in) -> Optional[models.Lead]:
    db_obj = get_lead(db, lead_id)
    if not db_obj:
        return None
    data = lead_in.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_lead(db: Session, lead_id: int) -> bool:
    db_obj = get_lead(db, lead_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True


def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    return schemas.DashboardStats(
        total_businesses=count_businesses(db),
        websites_found=count_websites_found(db),
        websites_audited=count_websites_audited(db),
        websites_with_issues=count_websites_with_issues(db),
        high_priority_leads=count_high_priority_leads(db),
        potential_monthly_revenue=potential_monthly_revenue(db),
    )
