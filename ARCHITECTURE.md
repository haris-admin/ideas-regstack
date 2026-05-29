# RegStack — Architecture & Module Structure

**Generated:** 30 May 2026

---

## Core Architecture Pattern

```
                 ┌──────────────────────┐
                 │   Business Profile   │
                 │   (Regulation Mapper)│
                 └────────┬─────────────┘
                          │
    ┌─────────────────────▼─────────────────────┐
    │            Compliance Engine               │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
    │  │ Workflow  │  │ Wizard   │  │ Scoring  │ │
    │  │ Engine    │  │ Builder  │  │ Engine   │ │
    │  └──────────┘  └──────────┘  └──────────┘ │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
    │  │ Document │  │ Deadline │  │ AI       │ │
    │  │ Manager  │  │ Tracker  │  │ Advisor  │ │
    │  └──────────┘  └──────────┘  └──────────┘ │
    └─────────────────┬────────────────────────┘
                      │
    ┌─────────────────▼────────────────────────┐
    │              Output Layer                  │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
    │  │ Regulator │  │ Audit    │  │ Evidence │ │
    │  │ Forms     │  │ Trail    │  │ Packs    │ │
    │  └──────────┘  └──────────┘  └──────────┘ │
    └─────────────────┬────────────────────────┘
                      │
    ┌─────────────────▼────────────────────────┐
    │             Delivery Layer                 │
    │  Web App  │  API  │  White-Label Widget   │
    └──────────────────────────────────────────┘
```

## Module Structure

### Regulation Modules (Pluggable)

Each regulation is a **config module** — not a code fork:

```
regstack/
├── core/                    # Shared engine
│   ├── engine/              # Workflow execution engine
│   ├── wizard/              # Form wizard framework
│   ├── document/            # Document upload & verification
│   ├── scoring/             # Risk scoring matrix
│   ├── audit/               # Immutable audit trail
│   ├── calendar/            # Deadline tracker
│   ├── ai/                  # RAG compliance advisor
│   └── api/                 # Public API layer
├── modules/
│   ├── aml/                 # AUSTRAC AML/CTF compliance
│   │   ├── config.yaml      # Regulation-specific rules, deadlines, forms
│   │   ├── workflows/       # CDD, SMR, TTR workflow definitions
│   │   ├── forms/           # PDF/API form templates
│   │   └── scoring/         # Industry-specific risk weightings
│   ├── boardproof/          # ASIC 12-point evidence packs
│   ├── bnpl/                # BNPL licensing & responsible lending
│   ├── fair-trading/        # Consumer protection per state
│   ├── privacy/             # Australian Privacy Principles
│   ├── insurance/           # Insurance distribution compliance
│   ├── npp/                 # PayTo/NPP compliance
│   └── sovereign-cyber/     # SOCI Act evidence packs
└── integrations/
    ├── greenid/             # Identity verification API
    ├── austrac/             # AUSTRAC report submission
    ├── xero/                # Transaction data pull
    ├── myob/                # Transaction data pull
    ├── asic/                # ASIC register lookups
    └── abr/                 # ABN/entity validation
```

## Technology Stack (Recommended)

| Layer | Technology | Rationale |
|:------|:-----------|:----------|
| **Frontend** | React + TypeScript | Component reuse, form-heavy UI |
| **Backend** | Python (FastAPI) or Node | FastAPI aligns with existing POCs |
| **Database** | PostgreSQL | Relational compliance data, ACID compliance |
| **Document store** | S3/MinIO | Encrypted document storage with retention policies |
| **Vector store** | ChromaDB/Pinecone | RAG for AI compliance advisor |
| **Workflow engine** | Custom lightweight (or Temporal) | Config-driven, not code-driven |
| **Identity** | Auth0 or Cognito | Multi-tenant SSO |
| **PDF generation** | WeasyPrint / Puppeteer | Regulator-formatted output |
| **CI/CD** | GitHub Actions | Already in use across fleet |

## Data Model (Core Entities)

```
┌─────────────┐       ┌─────────────────┐
│  Organisation│1───n│  Regulation_Scope│
└─────────────┘       └─────────────────┘
       │1                     │
       │                      │
┌──────▼──────┐     ┌─────────▼──────────┐
│   Users     │     │ Compliance_Records  │
└─────────────┘     └────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Documents  │
                    └─────────────┘
```

## API Design (Public)

```
GET  /v1/organisations/{id}/compliance-status
GET  /v1/organisations/{id}/deadlines
POST /v1/organisations/{id}/assessments
GET  /v1/organisations/{id}/reports/{type}
POST /v1/organisations/{id}/forms/{regulator}/submit
GET  /v1/modules                   # Available regulation modules
GET  /v1/modules/{id}/requirements # Requirements for a module
```

## Security & Compliance

- **Data residency:** AU-only (AWS ap-southeast-2)
- **Encryption:** AES-256 at rest, TLS 1.3 in transit
- **Audit trail:** Append-only, cryptographically linked
- **Retention:** Configurable per regulation (default 5 years)
- **Access control:** Role-based, per-organisation
- **Penetration testing:** Prior to Phase 1 launch
