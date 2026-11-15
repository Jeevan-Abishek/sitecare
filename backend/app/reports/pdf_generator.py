from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

from app.config import get_settings
from app.models import Business, Audit

settings = get_settings()

NAVY = HexColor("#0f172a")
NAVY_LIGHT = HexColor("#1e293b")
GREEN = HexColor("#16a34a")
ORANGE = HexColor("#ea580c")
RED = HexColor("#dc2626")
GRAY = HexColor("#64748b")
LIGHT_GRAY = HexColor("#f1f5f9")


def _styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=ss["Title"], fontSize=20, textColor=NAVY, spaceAfter=6, alignment=TA_LEFT),
        "subtitle": ParagraphStyle("subtitle", parent=ss["Normal"], fontSize=10, textColor=GRAY, spaceAfter=2),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13, textColor=NAVY, spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontSize=9.5, textColor=HexColor("#1e293b"), spaceAfter=4),
        "small": ParagraphStyle("small", parent=ss["Normal"], fontSize=8, textColor=GRAY),
        "cell": ParagraphStyle("cell", parent=ss["Normal"], fontSize=8.5, textColor=HexColor("#1e293b")),
        "cell_bold": ParagraphStyle("cell_bold", parent=ss["Normal"], fontSize=8.5, textColor=NAVY, fontName="Helvetica-Bold"),
    }


def generate_pdf_report(business: Business, audit: Audit | None, outreach=None) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title=f"Website Maintenance Audit - {business.business_name}",
        author=settings.AGENCY_NAME,
    )
    styles = _styles()
    story = []

    # Header band
    header_table = Table(
        [[
            Paragraph(f"<b>{settings.AGENCY_NAME}</b>", ParagraphStyle("brand", parent=styles["title"], fontSize=16, textColor=NAVY)),
            Paragraph(
                f"{settings.AGENCY_TAGLINE}<br/>"
                f"{settings.AGENCY_EMAIL} &nbsp;|&nbsp; {settings.AGENCY_PHONE or ''}",
                ParagraphStyle("brand_sub", parent=styles["subtitle"], fontSize=8),
            ),
        ]], colWidths=[100 * mm, 90 * mm]
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Report title
    story.append(Paragraph("Website Maintenance Audit Report", styles["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY))
    story.append(Spacer(1, 6))

    # Business info
    info_data = [
        [Paragraph("<b>Business</b>", styles["cell"]), Paragraph(business.business_name or "—", styles["cell"])],
        [Paragraph("<b>Category</b>", styles["cell"]), Paragraph(business.category or "—", styles["cell"])],
        [Paragraph("<b>Location</b>", styles["cell"]), Paragraph(f"{business.city or '—'}, {business.state or '—'} {business.country or '—'}", styles["cell"])],
        [Paragraph("<b>Website</b>", styles["cell"]), Paragraph(business.website or "—", styles["cell"])],
        [Paragraph("<b>Phone</b>", styles["cell"]), Paragraph(business.phone or "—", styles["cell"])],
        [Paragraph("<b>Email</b>", styles["cell"]), Paragraph(business.email or "—", styles["cell"])],
        [Paragraph("<b>Discovery Source</b>", styles["cell"]), Paragraph(f"{business.discovery_provider or 'manual'}", styles["cell"])],
    ]
    info_table = Table(info_data, colWidths=[40 * mm, 120 * mm])
    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # Audit summary
    story.append(Paragraph("Audit Summary", styles["h2"]))
    if audit:
        score = audit.score or 0
        issues = audit.verified_issues or []
        score_color = GREEN if score < 40 else (ORANGE if score < 70 else RED)
        score_style = ParagraphStyle("score", parent=styles["cell"], textColor=score_color, fontName="Helvetica-Bold", fontSize=14)

        summary_data = [
            [Paragraph("<b>Lead Score</b>", styles["cell"]), Paragraph(f"{score}/100", score_style)],
            [Paragraph("<b>Priority</b>", styles["cell"]), Paragraph(f"<b>{audit.audit_confidence or 'unknown'} confidence</b> &middot; {len(issues)} verified issue(s)", styles["cell"])],
            [Paragraph("<b>HTTP Status</b>", styles["cell"]), Paragraph(str(audit.http_status or "—"), styles["cell"])],
            [Paragraph("<b>Response Time</b>", styles["cell"]), Paragraph(audit.response_time or "—", styles["cell"])],
            [Paragraph("<b>SSL Status</b>", styles["cell"]), Paragraph("Valid" if (audit.ssl_status or {}).get("valid") else "Invalid/Missing", styles["cell"])],
            [Paragraph("<b>Last Audited</b>", styles["cell"]), Paragraph(audit.audit_date.strftime("%Y-%m-%d %H:%M") if audit.audit_date else "—", styles["cell"])],
        ]
        summary_table = Table(summary_data, colWidths=[40 * mm, 120 * mm])
        summary_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

        # Verified issues
        if issues:
            story.append(Paragraph("Verified Technical Issues", styles["h2"]))
            issue_rows = [[Paragraph("<b>#</b>", styles["cell_bold"]), Paragraph("<b>Issue</b>", styles["cell_bold"])]]
            for i, issue in enumerate(issues, 1):
                issue_rows.append([Paragraph(str(i), styles["cell"]), Paragraph(issue, styles["cell"])])
            issues_table = Table(issue_rows, colWidths=[10 * mm, 150 * mm])
            issues_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#fee2e2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
            ]))
            story.append(issues_table)
            story.append(Spacer(1, 10))

        # PageSpeed / Core Web Vitals
        if audit.pagespeed_metrics or audit.core_web_vitals:
            story.append(Paragraph("Performance &amp; Core Web Vitals", styles["h2"]))
            ps = audit.pagespeed_metrics or {}
            cwv = audit.core_web_vitals or {}
            perf_data = [
                [Paragraph("<b>Metric</b>", styles["cell_bold"]), Paragraph("<b>Value</b>", styles["cell_bold"])],
                [Paragraph("Performance Score", styles["cell"]), Paragraph(str(ps.get("performance_score") or "—"), styles["cell"])],
                [Paragraph("SEO Score", styles["cell"]), Paragraph(str(ps.get("seo_score") or "—"), styles["cell"])],
                [Paragraph("LCP (Largest Contentful Paint)", styles["cell"]), Paragraph(f'{cwv.get("LCP") or "—"} ms', styles["cell"])],
                [Paragraph("CLS (Cumulative Layout Shift)", styles["cell"]), Paragraph(str(cwv.get("CLS") or "—"), styles["cell"])],
                [Paragraph("TBT (Total Blocking Time)", styles["cell"]), Paragraph(f'{cwv.get("TBT") or "—"} ms', styles["cell"])],
                [Paragraph("FCP (First Contentful Paint)", styles["cell"]), Paragraph(f'{cwv.get("FCP") or "—"} ms', styles["cell"])],
            ]
            perf_table = Table(perf_data, colWidths=[70 * mm, 90 * mm])
            perf_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(perf_table)
            story.append(Spacer(1, 10))

        # Tech stack
        if audit.tech_stack:
            story.append(Paragraph("Technology Stack", styles["h2"]))
            ts = audit.tech_stack or {}
            ts_data = [
                [Paragraph("<b>CMS</b>", styles["cell"]), Paragraph(ts.get("cms") or "—", styles["cell"])],
                [Paragraph("<b>E-commerce</b>", styles["cell"]), Paragraph(ts.get("ecommerce") or "—", styles["cell"])],
                [Paragraph("<b>Frontend</b>", styles["cell"]), Paragraph(ts.get("frontend") or "—", styles["cell"])],
            ]
            ts_table = Table(ts_data, colWidths=[40 * mm, 120 * mm])
            ts_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(ts_table)
            story.append(Spacer(1, 10))

    else:
        story.append(Paragraph("No audit data available. Run a website audit first.", styles["body"]))

    # Recommended service
    story.append(Paragraph("Recommended Maintenance Service", styles["h2"]))
    if audit and audit.score is not None:
        from app.audit.scoring import service_for_flags, priority_for_score
        flags = {i.split(" ")[0].lower(): True for i in (audit.verified_issues or [])}
        service = service_for_flags(flags, audit.score or 0)
        priority = priority_for_score(audit.score or 0)
        story.append(Paragraph(f"<b>{service}</b> &nbsp;|&nbsp; <b>{priority.upper()} priority</b>", styles["body"]))
    else:
        story.append(Paragraph("Run an audit to get a service recommendation.", styles["body"]))
    story.append(Spacer(1, 10))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by {settings.AGENCY_NAME} &mdash; {settings.AGENCY_TAGLINE}<br/>"
        f"{settings.AGENCY_EMAIL} &nbsp;|&nbsp; {settings.AGENCY_PHONE or ''} &nbsp;|&nbsp; {settings.AGENCY_WEBSITE}",
        ParagraphStyle("footer", parent=styles["small"], alignment=TA_CENTER),
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
