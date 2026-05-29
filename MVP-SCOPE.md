# RegStack — Weekend MVP Scope (AUSTRAC Tranche 2)

**Build window:** Weekend of 30-31 May 2026
**Deadline:** AUSTRAC Tranche 2 compliance by 1 July 2026 (32 days)

---

## MVP Scope

A **guided compliance wizard** for real estate agents to complete their AUSTRAC AML/CTF obligations.

### What It Does

1. **Business profile** — Agent enters their agency details
2. **CDD wizard** — Step-by-step customer due diligence guided form
3. **Risk scoring** — Auto-calculates customer risk level based on inputs
4. **AUSTRAC report** — Generates downloadable SMR/TTR forms
5. **Audit trail** — Logs all actions with timestamps

### What It Does NOT Do (Phase 2+)

- ❌ Multi-regulation (future)
- ❌ AI compliance advisor (future)
- ❌ API for partners (future)
- ❌ White-label (future)

### Tech Stack (MVP)

- **Frontend:** Single HTML page with embedded JS (no build step)
- **Backend:** Python Flask/FastAPI
- **Storage:** SQLite (local, upgrade to PostgreSQL later)
- **Auth:** Simple email + magic link
- **Export:** PDF via WeasyPrint
- **Hosting:** AWS EC2 or Render

### MVP Screens

| Screen | Purpose | Fields |
|:-------|:--------|:-------|
| /onboard | Business profile | Business name, ABN, address, industry (real estate), services offered, estimated transactions/mo |
| /cdd/new | Customer due diligence form | Customer name, DOB, address, ID type, ID number, ID expiry, relationship type, transaction purpose, source of funds |
| /risk/:customer_id | Risk assessment | Auto-calculated from CDD inputs + override |
| /report | AUSTRAC report generation | Select date range, generate SMR/TTR, preview, download PDF |
| /audit | Audit trail view | Filterable list of all actions with timestamps |
| /dashboard | Summary | Active customers, upcoming deadlines, risk distribution |

### Data Model (MVP)

```sql
-- Organisations
CREATE TABLE organisations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    abn TEXT,
    industry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers (CDD records)
CREATE TABLE customers (
    id TEXT PRIMARY KEY,
    org_id TEXT REFERENCES organisations(id),
    name TEXT NOT NULL,
    dob DATE,
    id_type TEXT,
    id_number TEXT,
    id_expiry DATE,
    risk_score TEXT CHECK(risk_score IN ('low','medium','high')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE audit_log (
    id TEXT PRIMARY KEY,
    org_id TEXT REFERENCES organisations(id),
    user_id TEXT,
    action TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    org_id TEXT REFERENCES organisations(id),
    type TEXT CHECK(type IN ('smr','ttr','compliance')),
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Build Order (Weekend)

- **Day 1 (Sat):** Backend (models, API endpoints, form generation)
- **Day 2 (Sun):** Frontend (screens, integration), deploy

### Weekend MVP Go/No-Go

- ✅ We can build this weekend IF the core form-to-output pipeline can be completed
- ❌ We should NOT try to build GreenID integration this weekend (use manual ID entry)
- ✅ We CAN deliver a working prototype that generates AUSTRAC-ready PDFs
