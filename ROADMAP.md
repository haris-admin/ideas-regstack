# RegStack — 3-Phase Build Roadmap

**Generated:** 30 May 2026
**Target launch:** Phase 1 MVP by 30 June 2026 (in time for AUSTRAC Tranche 2)

---

## Phase 1: AML Core + Workflow Builder (Months 1-3)

**Target:** 15,000 real estate offices needing AUSTRAC Tranche 2 compliance by 1 July

### Milestones

| Week | Deliverable | Dependencies |
|:-----|:------------|:-------------|
| W1 | Business Profile Wizard (P1-F1) | None |
| W2 | AML CDD Workflow Builder v1 (P1-F2) | W1 |
| W3 | GreenID API integration (P1-F4) | W2 |
| W3 | AUSTRAC report generation (P1-F3) | W2 |
| W4 | Risk scoring matrix (P1-F5) | W2 |
| W4 | Audit trail storage (P1-F6) | None |
| W5 | Compliance calendar (P1-F7) | W1 |
| W6 | Team & role management (P1-F8) | W1 |
| W7-8 | Integration testing + security audit | W1-6 |
| W9-10 | Beta with 10 real estate offices | W7-8 |
| W11 | Fixes + polish | W9-10 |
| **W12** | **🔴 Phase 1 Launch — AUSTRAC Tranche 2 deadline** | W11 |

### Phase 1 Technical Scope

- **Frontend:** React SPA — 6 screens (Profile, CDD, Reports, Calendar, Documents, Settings)
- **Backend:** FastAPI — 15 endpoints
- **Integrations:** GreenID (identity), AUSTRAC (reporting), ABR (entity lookup)
- **Database:** PostgreSQL + S3 for documents
- **Auth:** Multi-tenant, role-based

### Phase 1 Pricing

| Tier | Price | Features |
|:-----|:------|:---------|
| AML Starter | $149/mo | Single regulation (AML only), 1 user, 50 checks/mo |
| AML Pro | $249/mo | AML + calendar, 3 users, 200 checks/mo, risk scoring |

---

## Phase 2: Multi-Regulation + Intelligence (Months 4-6)

### Milestones

| Month | Deliverable |
|:------|:------------|
| M4 | BNPL licensing workflow module |
| M4 | AI Compliance Advisor (RAG engine) — Beta |
| M5 | Regulatory update feed |
| M5 | Fair trading / consumer protection checklists |
| M6 | Compliance Score Dashboard |
| M6 | Evidence Pack Generator |
| **M6** | **🔴 Phase 2 Launch** |

### Phase 2 Technical Scope

- AI RAG engine with ChromaDB/Pinecone
- Regulation-as-config framework (YAML-defined module schema)
- Consumer protection rules engine per state
- PDF evidence pack generation

### Phase 2 Pricing

| Tier | Price | Features |
|:-----|:------|:---------|
| Growth | $249/mo | 2-3 regulations, 3 users, 200 checks/mo, AI advisor |

---

## Phase 3: Platform + Partners (Months 7-12)

### Milestones

| Month | Deliverable |
|:------|:------------|
| M7 | Public API — compliance status, deadline check, form generation |
| M7 | Xero/MYOB plugin — MVP |
| M8 | White-label for industry associations |
| M8 | PayTo compliance module |
| M9 | Insurance distribution module |
| M10 | Privacy Act compliance module |
| M11-12 | Cross-jurisdiction module (AU-EU, AU-UK) |
| **M12** | **🔴 Phase 3 Launch** |

### Phase 3 Pricing

| Tier | Price | Features |
|:-----|:------|:---------|
| Scale | $499/mo | 4+ regulations, unlimited users, API access, white-label |
| Enterprise | Custom | Embedded/SLA, dedicated support, custom integrations |

---

## Build Dependencies

| External | Status | Notes |
|:---------|:-------|:------|
| GreenID API access | Requires signup | Free tier available for testing |
| AUSTRAC API access | Requires registration | File upload available without API |
| ASIC register API | Public | Free tier |
| ABR API | Public | Free tier |
| Xero API access | Requires Xero app | Easy — developer account |
| ChromaDB | Already running | In fleet infrastructure |

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|:-----|:-----------|:-------|:-----------|
| AUSTRAC delays Tranche 2 enforcement | Low | Medium | Launch anyway — early market advantage |
| FrankieOne pivots down-market | Medium | High | Build differentiation on multi-regulation + workflow |
| Xero builds compliance module | Low-Medium | Medium | Partner early, differentiate on depth |
| AI Advisor hallucinates regulation | Medium | High | RAG with strict citation, human-in-loop for critical answers |
| Phase 1 misses 1 July deadline | Medium | Critical | Scope to MVP-only features, defer team management |
