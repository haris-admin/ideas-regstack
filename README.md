# RegStack — Multi-Regulation SME Compliance Platform

**Score:** 92/100 (Rank #1)
**Tagline:** "Stripe Atlas for SME Compliance"
**AU TAM:** ~$540M (180,000 regulated SMEs × $149–499/mo)

---

## What It Is

An end-to-end compliance workflow engine for Australian SMEs across real estate, legal, accounting, BNPL lenders, payment facilitators, and insurers. One platform, all regulations, auto-updating.

## Why Now

Multiple regulatory deadlines are converging simultaneously:

| Deadline | Regulation | Impact |
|----------|-----------|--------|
| 1 July 2026 | AUSTRAC Tranche 2 | 15,000+ real estate offices need AML compliance |
| 30 June 2026 | ASIC Digital Assets | Crypto/BNPL licensing requirements |
| In-flight | CPS 230 | Operational risk management for APRA-regulated entities |
| In-flight | Screen-scraping sunset | Banking data access changes |
| TBD 2026 | AU AI Mandatory Guardrails | AI governance requirements |

**The incumbent is spreadsheets + Word docs + email** — 60%+ of the SME market.

## Quick Start

### Prerequisites
- Python 3.11+

### 1. Clone & Set Up Database
```bash
git clone https://github.com/haris-admin/ideas-regstack.git
cd ideas-regstack

# Set up local SQLite database (dev)
python db/migrate.py

# Verify schema
python db/migrate.py --verify
```

### Supabase Staging/Production
```bash
python db/migrate.py --to-pg --url "postgresql://user:pass@db.xxx.supabase.co:5432/postgres"
```

## Database

| Environment | Engine | How to set up |
|-------------|--------|---------------|
| **Dev (local)** | SQLite | `python db/migrate.py` |
| **Staging/Prod** | Supabase (PostgreSQL) | `python db/migrate.py --to-pg --url <supabase-url>` |

### Tables
- `regulations` — Regulatory obligations (jurisdiction, category, effective date)
- `entities` — Regulated entities being tracked
- `assessments` — Compliance assessments (entity × regulation × status)
- `submissions` — Regulatory submissions and filings
- `audit_trail` — Compliance audit log
- `deadlines` — Upcoming compliance deadlines and reminders

## Repo Structure

```
ideas-regstack/
├── README.md              # This file
├── db/
│   ├── migrate.py         # Standalone DB migration
│   ├── schema.sql         # Full DDL
│   └── README.md          # DB setup instructions
├── STACK.md               # ✅ Confirmed tech stack (Python/Next.js/Supabase/R2/Vercel)
├── docs/                  # Coming soon
└── requirements.txt       # Python dependencies
```
