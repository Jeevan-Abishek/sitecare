from datetime import datetime
from urllib.parse import quote

from app.schemas import OutreachGenerate, OutreachResult
from app.models import Business, Audit
from app.database import SessionLocal


def _issue_summary(issues: list) -> str:
    if not issues:
        return "No major verified issues."
    return "; ".join(issues[:5])


def generate_outreach(business: Business, audit: Audit | None, req: OutreachGenerate) -> OutreachResult:
    name = business.business_name or "there"
    website = business.website or "your website"
    phone = business.phone or ""
    email = business.email or ""
    score = audit.score if audit else 0
    issues = audit.verified_issues if audit and audit.verified_issues else []
    service = "website maintenance"
    if audit:
        from app.audit.scoring import service_for_flags
        flags = {i.split(" ")[0].lower(): True for i in issues}
        service = service_for_flags(flags, score)

    whatsapp = None
    if req.include_whatsapp:
        whatsapp = (
            f"Hi {name}, I'm reaching out from SiteCare AI. I ran a free technical check on "
            f"{website} and found {len(issues)} verified issue(s) (score {score}/100), including: "
            f"{_issue_summary(issues)}. We offer {service} tailored for {business.category or 'local'} "
            f"businesses in {business.city or 'your area'}. Would you like a free audit summary? "
            f"Reply to this message or contact us. - SiteCare AI Team"
        )

    email_subject = None
    email_body = None
    if req.include_email:
        email_subject = f"Free website audit for {business.business_name or 'your business'} ({score}/100)"
        email_body = (
            f"Dear {name},\n\n"
            f"I recently reviewed {website} as part of a local business website health check. "
            f"Our audit identified {len(issues)} verified technical issue(s) giving the site a score of "
            f"{score}/100.\n\nKey findings:\n{_issue_summary(issues)}\n\n"
            f"We recommend {service}. This can improve reliability, mobile experience, and search visibility "
            f"for customers in {business.city or 'your area'}.\n\n"
            f"I'd be happy to share the full audit report and a proposal at no obligation.\n\n"
            f"Best regards,\nSiteCare AI Team\n"
            f"{business.phone or ''}"
        )

    proposal = None
    if req.include_proposal:
        proposal = (
            f"Website Maintenance Proposal\nPrepared for: {business.business_name}\n"
            f"Website: {website}\nLocation: {business.city}, {business.state} {business.country}\n\n"
            f"Current lead score: {score}/100 ({priority_label(score)} priority)\n"
            f"Verified issues found: {len(issues)}\n{_issue_summary(issues)}\n\n"
            f"Recommended service: {service}\n\n"
            f"Package includes: ongoing monitoring, SSL management, broken-link repair, "
            f"mobile-viewport fixes, metadata optimization, and monthly reporting.\n"
            f"Pricing is scoped after a full site review. Contact us to get started."
        )

    followup = None
    if req.include_followup:
        followup = (
            f"Hi {name}, following up on my earlier message about {website}. "
            f"I'd love to share the free audit summary and discuss how {service} could help "
            f"your business. No obligation—just reply when convenient. - SiteCare AI"
        )

    audit_summary = None
    if audit:
        audit_summary = (
            f"Audit Summary for {website}\nScore: {score}/100\nPriority: {priority_label(score)}\n"
            f"Issues: {len(issues)}\n{_issue_summary(issues)}\nRecommended: {service}\n"
            f"Audited: {audit.audit_date.strftime('%Y-%m-%d') if audit.audit_date else 'N/A'}"
        )

    # Build direct action links
    whatsapp_url = None
    if whatsapp and business.phone:
        # Strip non-digits from phone for wa.me
        digits = "".join(c for c in business.phone if c.isdigit() or c == "+")
        whatsapp_url = f"https://wa.me/{digits}?text={quote(whatsapp)}"

    email_mailto = None
    if email_body and business.email:
        subject_quote = quote(email_subject or "Website Maintenance Audit")
        body_quote = quote(email_body)
        email_mailto = f"mailto:{business.email}?subject={subject_quote}&body={body_quote}"

    return OutreachResult(
        business_id=business.id,
        whatsapp_message=whatsapp,
        whatsapp_url=whatsapp_url,
        email_subject=email_subject,
        email_body=email_body,
        email_mailto=email_mailto,
        proposal=proposal,
        followup_message=followup,
        audit_summary=audit_summary,
    )


def priority_label(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"
