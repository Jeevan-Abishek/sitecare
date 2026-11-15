# SiteCare AI – Website Maintenance Lead Finder

A complete, zero-budget, full-stack web application that discovers business websites, audits their technical health, identifies **verified** problems, and generates qualified sales leads for website maintenance services.

## What it does

1. **Lead discovery** – Find businesses by country/state/city/category using the free OpenStreetMap Overpass API (default: Tamil Nadu, India). Also import leads via CSV or add website URLs manually.
2. **Website audit** – For each website, verify: HTTP status/reachability, SSL certificate validity, response time, redirect problems, broken internal/external links, missing page title/meta description/favicon/mobile viewport, missing image alt attributes, placeholder/lorem content, outdated copyright dates. Only actually-verified issues are reported.
3. **Lead scoring** – 0–100 score from verified issues (unavailable +20, invalid SSL +20, broken internal links +20, missing mobile viewport +15, slow response +10, placeholder content +10, missing metadata +5, etc.). High/Medium/Low priority.
4. **Lead management** – Dashboard cards, searchable/sortable/filterable/paginated lead table, lead details, audit history, CSV export, delete, mark contacted/interested/converted, personal notes.
5. **AI report generator** – Free, local rules-based report generator (default). Explains verified problems in simple language, recommends services, suggests a maintenance package. External LLM integration is optional and never required.
6. **Outreach generator** – WhatsApp message, professional email, maintenance proposal, audit summary, follow-up message. Uses only publicly listed contact info. Never sends automatically.

## Advanced Production Features

7. **Google Places / Maps Discovery** – Optional Google Places API (New) provider alongside OpenStreetMap. Captures precise business names, phone numbers, addresses, and official websites. Configurable via `GOOGLE_PLACES_API_KEY`. Falls back gracefully when key is not configured.

8. **Google PageSpeed Insights & Core Web Vitals** – Optional PageSpeed Insights integration fetches real mobile performance scores, SEO scores, and Core Web Vitals (LCP, CLS, TBT, FCP). Configurable via `GOOGLE_PAGESPEED_API_KEY`. Skipped gracefully when key is not configured.

9. **Branded PDF Report Generator** – ReportLab-powered PDF reports with agency branding, audit summary, verified issues, performance metrics, Core Web Vitals, and technology stack. Downloadable via `GET /api/reports/{id}/pdf` and "Download PDF Report" buttons in the UI.

10. **One-Click WhatsApp & Email Outreach** – Direct `wa.me` links with pre-filled message templates and `mailto` links with pre-filled subject/body. Messages are generated locally and never sent automatically. Optional SMTP support for direct email dispatch.

11. **Tech Stack Detector** – Identifies CMS (WordPress, Shopify, Wix, Squarespace, Joomla, Drupal), e-commerce platforms, and frontend frameworks (React, Next.js, Vue, Angular) from HTML and headers. Falls back to "Custom HTML" when none detected.

12. **Mobile Preview** – Responsive mobile simulator card in Lead Detail view showing how the target website renders on a mobile device.

13. **Automated Uptime & SSL Expiry Monitor** – Background scheduler (APScheduler) periodically checks saved websites for uptime status and SSL certificate expiry. Dashboard badges flag sites that are down or have SSL expiring within the configured warning period (default 30 days) for retainer pitching.


## Tech stack

- **Frontend:** React, TypeScript, Tailwind CSS, Lucide icons, React Router, Vite
- **Backend:** Python FastAPI, SQLAlchemy ORM, SQLite, Pydantic, httpx, BeautifulSoup
- **Auditing:** httpx/requests, BeautifulSoup, SSL verification, broken-link detection, response-time measurement, mobile-viewport detection
- **Discovery:** OpenStreetMap Overpass API (modular provider)

## Zero-budget

No paid APIs, subscriptions, or services are required:
- SQLite database (local file)
- OpenStreetMap Overpass API (free)
- Free Python libraries
- Local rules-based AI analysis
- Local deployment + Docker

## Project layout

```
/workspace/app
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app + middleware
│   │   ├── database.py      # SQLite + SQLAlchemy session
│   │   ├── models.py        # Business, Audit, Lead models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Data access
│   │   ├── security.py      # SSRF protection, URL validation
│   │   ├── deps.py          # DB + rate limiting
│   │   ├── config.py        # Settings
│   │   ├── discovery/       # Modular lead discovery (Overpass)
│   │   ├── audit/           # Website audit engine + scoring
│   │   ├── reports/         # Rules-based AI report generator
│   │   ├── outreach.py      # Outreach message generator
│   │   └── api/v1/          # REST endpoints
│   ├── tests/               # Pytest suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                # React + TypeScript + Vite + Tailwind
│   ├── src/
│   │   ├── App.tsx
│   │   ├── lib/api.ts       # API client
│   │   ├── lib/constants.ts
│   │   ├── components/layout.tsx
│   │   ├── components/ui.tsx
│   │   ├── pages/           # Dashboard, FindBusinesses, WebsiteAudits, QualifiedLeads, LeadDetail, OutreachGenerator, Reports, Settings
│   │   ├── index.css
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/discover` | Discover businesses via Overpass (filters: country, state, city, category, limit) |
| POST | `/api/audit` | Audit a single website (auto-creates business + lead) |
| POST | `/api/audit/bulk` | Audit multiple websites |
| GET | `/api/businesses` | List businesses (search, category, city) |
| POST | `/api/businesses` | Add a business manually |
| POST | `/api/import/csv` | Import businesses from CSV |
| GET | `/api/leads` | List leads (search, category, city, priority, status, pagination) |
| GET | `/api/leads/{id}` | Get a lead with business + audit |
| PATCH | `/api/leads/{id}` | Update lead status/notes |
| DELETE | `/api/leads/{id}` | Delete a lead |
| GET | `/api/reports` | List audit reports |
| GET | `/api/reports/{id}` | Get report for a business |
| GET | `/api/export/csv` | Export leads to CSV |
| POST | `/api/outreach/generate` | Generate WhatsApp/email/proposal/follow-up for a lead |

## Security

- URLs validated; only http/https allowed
- localhost, private IPs (RFC 1918), link-local, and internal hostnames blocked (SSRF protection)
- Configurable crawl depth/page limits, request timeouts, concurrent-request limits
- Input validation via Pydantic; rate limiting on all endpoints
- No secrets stored; only public business contact information used

## Quick start (local)

### Backend

```bash
cd backend
pip install -r requirements.txt   # (or pip3 install --break-system-packages -r requirements.txt)
cp .env.example .env
python3 -m uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev        # dev server on http://localhost:5173 (proxies /api to backend)
npm run build      # production build
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

### Run tests

```bash
cd backend
python3 -m pytest tests/
```

## Docker (optional)

```bash
docker-compose up --build
```
- Backend: `http://localhost:8000`
- Frontend (nginx): `http://localhost`

Data persists in the `sitecare_data` Docker volume.

## Discovery coverage & limitations

Business discovery uses the OpenStreetMap Overpass API. Coverage depends on OSM data in the selected area:
- Not all businesses are mapped in OSM.
- Not all mapped businesses have a website or phone/email.
- Results are a sample, not a complete business registry.
- The Overpass provider is modular (`app/discovery/overpass.py`, `BaseDiscoveryProvider`) so additional search APIs can be added later.

If the discovery provider is unavailable, the API returns a clear error and points to the offline alternatives: CSV import (`/api/import/csv`) and manual website audit (`/api/audit`).

## Lead scoring (verified issues only)

| Issue | Points |
|-------|--------|
| Website unavailable | +20 |
| Invalid SSL | +20 |
| Broken internal links | +20 |
| Missing mobile viewport | +15 |
| Slow response time (>3s) | +10 |
| Placeholder / lorem content | +10 |
| Missing metadata (title or description) | +5 |
| Missing favicon | +3 |
| Broken images | +3 |
| Broken external links | +3 |
| Outdated copyright | +2 |

Score capped at 100. Related issues are not double-counted.
- High priority: score ≥ 70
- Medium priority: score ≥ 40
- Low priority: score < 40

A high score means more verified technical issues — not confirmed buying intent.

## AI report generator

Default: a free local rules-based generator (`app/reports/generator.py`). No OpenAI/Anthropic key required.
External LLM integration (`LLM_PROVIDER=openai\|anthropic`) is optional; the app falls back to rules if it is unavailable or misconfigured.

## Crawl etiquette

- Respects `robots.txt` spirit via conservative limits
- Configurable page limit per domain (default 10), depth (default 2)
- 15s request timeout, 4 concurrent requests max
- SSRF protection; only public http/https URLs crawled

## Notes

- Audit results are genuine (live checks against real websites). No fake demo data is presented as real leads.
- Demo/sample data, if added, is clearly labelled.
- Messages are generated locally and never sent automatically.
