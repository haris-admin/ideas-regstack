# RegStack — Technology Stack (Confirmed)

**Last Updated:** 30 May 2026
**Source:** Haris (Fleet Commander)

---

## Confirmed Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Frontend** | **Next.js** (React, TypeScript) | Web application UI |
| **Backend** | **Python** (FastAPI) | API server, business logic, risk engine |
| **Database** | **Supabase** (PostgreSQL 15+) | Staging + Production |
| **Auth** | **Supabase Auth** | User authentication, org management |
| **Storage** | **Cloudflare R2** | Document storage, evidence files, report hosting |
| **Hosting** | **Vercel** (preferred) or **Netlify** | Frontend deployment |
| **Runtime** | **Bun** (alternative, per-project fit) | JavaScript runtime where appropriate |

---

## Layer Details

### Frontend — Next.js
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS or shadcn/ui
- **State:** React Context + SWR/React Query for API calls
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts for compliance dashboards
- **Deployment:** Vercel (preferred)
- **Alternative:** Netlify if Vercel pricing is prohibitive

### Backend — Python (FastAPI)
- **Framework:** FastAPI (async-first)
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0 (async) for Supabase queries
- **Validation:** Pydantic v2 (built into FastAPI)
- **API Style:** RESTful, auto-generated OpenAPI docs
- **Client:** Supabase Python SDK for direct queries
- **Auth:** Supabase Auth JWT verification middleware
- **Tasks:** Background task queue (Celery or Arq) for report generation
- **Hosting:** Same VPS/container as the API, or serverless

### Database — Supabase (PostgreSQL)
- **Provider:** Supabase (both staging and production)
- **Extensions:** pgcrypto, uuid-ossp
- **Migrations:** Numbered SQL files in `db/migrations/`
- **RLS:** Row Level Security for multi-tenant isolation
- **Backups:** Supabase automatic daily backups
- **Local dev:** Supabase CLI (`supabase start` for local instance)

### Storage — Cloudflare R2
- **Service:** Cloudflare R2 (S3-compatible)
- **Use cases:** Customer ID documents, compliance evidence, generated PDF reports, audit trail exports
- **Access:** Direct S3 API via `boto3` (Python)
- **Pricing:** Free tier (10 GB storage, 1M operations/mo)
- **Alternative:** Supabase Storage Buckets (if R2 free tier insufficient)

### Hosting — Vercel or Netlify
- **Primary:** Vercel (for Next.js, free hobby tier may need upgrade)
- **Alternative:** Netlify
- **Note:** Hobby projects not allowed for commercial use — may need Pro plan (~$20/mo)

### Runtime Alternative — Bun
- **When to use:** If a component makes sense as JavaScript (e.g., edge functions, build-time scripts, lightweight APIs)
- **When NOT to use:** For the main backend API (Python preferred)
- **Integration:** Bun can run Next.js dev server and some API routes

---

## Architectural Decisions

### AD-001: Supabase for Both Staging and Production
- Single Supabase project with separate schemas or separate projects for staging/prod
- **Chosen:** Separate Supabase projects (staging = free tier, prod = paid tier)
- Migration scripts run against both environments

### AD-002: R2 Over Supabase Storage
- Cloudflare R2 for document/evidence storage
- Free tier: 10 GB storage, 1M operations/month
- No egress fees (unlike S3)
- Supabase Storage is available as fallback if R2 doesn't suit

### AD-003: Vercel Over Netlify
- Vercel is the Next.js native platform (created by same team)
- Better DX for Next.js deployments
- Netlify is acceptable if Vercel Pro pricing ($20/mo) is a concern

### AD-004: Python Over Bun for Backend
- Python has richer libraries for compliance work (PDF generation, data validation, ML for risk scoring)
- Pydantic's automatic data validation is critical for compliance accuracy
- Zero Lang explored as CLI admin tool option (2 KB binary, no deps)

### AD-005: PostgreSQL Over SQLite
- Supabase uses PostgreSQL natively
- Full SQL feature set, JSONB for flexible metadata
- Row Level Security for multi-tenant data isolation
- Built-in vector support for future AI features

---

## Dev Environment

### Local Development
```
Frontend:  npm run dev  →  localhost:3000
Backend:   uvicorn regstack_server:app --reload  →  localhost:8000
Database:  Supabase CLI (supabase start)  →  localhost:54322
Storage:   MinIO (local R2-compatible)  →  localhost:9000
```

### Commands
```bash
# Frontend
cd frontend
npm install
npm run dev          # Development
npm run build        # Production build

# Backend
cd backend
poetry install       # or pip install -r requirements.txt
uvicorn main:app --reload

# Database
supabase start       # Local Supabase
supabase db push     # Apply migrations
supabase db pull     # Sync local schema from remote

# Storage (local MinIO for R2)
docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
```

---

## Deployment Pipeline

```
Git Push (main) → GitHub Actions →
  1. Run tests (pytest + jest)
  2. Build frontend (next build)
  3. Run database migrations
  4. Deploy frontend to Vercel
  5. Deploy backend to server/container
  6. Seed demo data
  7. Health check → ✓ Alert on Telegram
```

---

## Chronological Plan

| Date | Milestone |
|:-----|:----------|
| Wk 1 | Supabase project setup + migrations applied |
| Wk 1 | Backend: FastAPI + Supabase client + auth |
| Wk 2 | Frontend: Next.js scaffold + org onboarding |
| Wk 2 | Risk scoring engine (live, not CLI) |
| Wk 3 | CDD wizard + AUSTRAC report generation |
| Wk 4 | R2 storage integration + document upload |
| Wk 5-6 | Compliance dashboard + deadline tracker |
| Wk 7-8 | Multi-tenant isolation (RLS) + audit trail |
| Wk 9-10 | Beta with 5 real estate offices |
| Wk 11 | Fixes + polish |
| **Wk 12** | **🚀 Phase 1 Launch — AUSTRAC Tranche 2** |
