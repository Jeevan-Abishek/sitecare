from datetime import datetime

from app.schemas import ReportGenerate, ReportOut
from app.models import Business, Audit, Lead
from app.database import SessionLocal
from app.audit.scoring import priority_for_score, service_for_flags


def _issue_list(issues: list) -> str:
    if not issues:
        return "No verified issues were detected."
    return "\n".join(f"- {issue}" for issue in issues)


def generate_rules_report(business: Business, audit: Audit | None) -> str:
    name = business.business_name or "this business"
    city = business.city or "the area"
    category = business.category or "business"
    website = business.website or "no website listed"
    score = audit.score if audit else 0
    issues = audit.verified_issues if audit and audit.verified_issues else []
    confidence = (audit.audit_confidence if audit else "unknown") or "unknown"
    last_audit = audit.audit_date.strftime("%Y-%m-%d") if audit and audit.audit_date else "not audited"

    lines = []
    lines.append(f"Website Maintenance Audit Report")
    lines.append(f"=" * 40)
    lines.append(f"Business: {name}")
    lines.append(f"Category: {category}")
    lines.append(f"Location: {city}")
    lines.append(f"Website: {website}")
    lines.append(f"Lead Score: {score}/100")
    lines.append(f"Priority: {priority_for_score(score).upper()}")
    lines.append(f"Audit Confidence: {confidence}")
    lines.append(f"Last Audit: {last_audit}")
    lines.append("")
    lines.append("Verified Problems:")
    lines.append(_issue_list(issues))
    lines.append("")
    lines.append("Recommended Maintenance Service:")
    flags = {i.split(" ")[0].lower(): True for i in issues}
    lines.append(f"- {service_for_flags(flags, score)}")
    lines.append("")
    lines.append("What this means:")
    if score >= 70:
        lines.append("This website has multiple verified technical issues. A full maintenance")
        lines.append("package (repair, SSL, performance, mobile readiness) is strongly recommended.")
    elif score >= 40:
        lines.append("This website has several issues worth addressing. A maintenance package")
        lines.append("can prevent further deterioration and improve reliability.")
    else:
        lines.append("This website is in relatively good health. Periodic monitoring and")
        lines.append("light maintenance are recommended.")
    lines.append("")
    lines.append("All findings above are based on verified checks performed on the live website.")
    lines.append("No assumptions are made about plugins, hosting, or security beyond what was tested.")
    return "\n".join(lines)


def generate_report(business: Business, audit: Audit | None, provider: str = "rules") -> ReportOut:
    if provider != "rules":
        # External LLM optional; fall back to rules if unavailable
        try:
            body = _generate_llm_report(business, audit, provider)
        except Exception:
            body = generate_rules_report(business, audit)
            provider = "rules"
    else:
        body = generate_rules_report(business, audit)

    return ReportOut(
        business_id=business.id,
        report_title=f"Website Maintenance Audit - {business.business_name}",
        report_body=body,
        generated_at=datetime.utcnow(),
        provider=provider,
    )


def _generate_llm_report(business: Business, audit: Audit | None, provider: str) -> str:
    """Optional external LLM integration. Not required for the app to work."""
    raise NotImplementedError(f"LLM provider '{provider}' not implemented; using rules-based report")
