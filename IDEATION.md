# RegStack — Feature Requirements & Ideation

**Generated:** 30 May 2026
**Source:** Gumby analysis, Genspark Startup Recommendations v2 (22 May), Pluto research, MVP-Week22 synthesis
**Status:** Ideation — pre-build

---

## Core Concept

A configurable compliance workflow engine that lets SMEs:
1. Know **which regulations apply** to their business
2. **Complete their obligations** through guided wizards
3. **Generate regulator-ready outputs** (forms, evidence packs, reports)
4. **Track deadlines** across all regulators in one view

**Pattern:** Form → Engine → Output — same architecture, different regulation modules.

---

## Feature Catalog

### PHASE 1: AML Core + Workflow Builder (Months 1-3)

#### P1-F1: Business Profile Wizard
- **Description:** Guided onboarding that determines which regulations apply
- **Inputs:** Business type, industry, size, services offered, states operating in
- **Outputs:** Compliance scorecard, regulation checklist, deadline calendar
- **Key UX:** 5-minute setup, saves answers for future updates

#### P1-F2: AML CDD Workflow Builder
- **Description:** Configurable no-code workflow for Customer Due Diligence
- **Steps:** Identify customer → Verify identity (GreenID API) → Risk score → Ongoing monitoring schedule
- **Outputs:** Completed CDD record, risk assessment matrix
- **SME-specific:** Real estate agent template, legal practitioner template, accountant template

#### P1-F3: AUSTRAC Reporting Auto-Generation
- **Description:** Auto-fills and generates AUSTRAC compliance reports
- **Report types:** SMR (Suspicious Matter Report), TTR (Threshold Transaction Report), Compliance Report
- **Integration:** API push to AUSTRAC (or downloadable PDF for manual filing)
- **Smart fill:** Pulls from CDD records + transaction data

#### P1-F4: Document Upload & Verification
- **Description:** Customer document collection with identity verification
- **Providers:** GreenID API or alternative (FrankieOne, Onfido)
- **Types:** Passport, license, company extract, trust deed
- **Storage:** Encrypted, audit-trailed, AUSTRAC-retention-compliant

#### P1-F5: Risk Scoring Matrix
- **Description:** Configurable risk scoring by industry and customer type
- **Factors:** Jurisdiction, transaction volume, customer type, product risk
- **Outputs:** Low/Medium/High risk rating with rationale
- **Customisation:** Industry-specific weightings

#### P1-F6: Audit Trail Storage
- **Description:** Immutable audit trail for all compliance actions
- **Storage:** Append-only log with timestamps, user, action
- **Retention:** Configurable per regulation (5 years default for AML)
- **Export:** Board-ready evidence packs in PDF

#### P1-F7: Compliance Calendar & Deadline Tracker
- **Description:** Auto-updating calendar of all regulatory deadlines
- **Sources:** Curated from ASIC, APRA, AUSTRAC, DTA, ATO, AFCA
- **Personalisation:** Filters by business type and active regulations
- **Notifications:** 30-day, 7-day, 1-day warnings via email/in-app

#### P1-F8: Team & Role Management
- **Description:** Multi-user access with role-based permissions
- **Roles:** Admin, Compliance Officer, Contributor, Auditor
- **Features:** Action assignment, approval workflows, delegation

### PHASE 2: Multi-Regulation + Intelligence (Months 4-6)

#### P2-F1: BNPL Licensing Workflow
- **Description:** Workflow templates for BNPL/AFSL licensing applications
- **Covers:** Credit license application, responsible lending obligations, ASIC reporting
- **Templates:** Hardship policy, consumer protection checklist, dispute resolution

#### P2-F2: AI Compliance Advisor (RAG Engine)
- **Description:** LLM-powered Q&A over ASIC, AUSTRAC, APRA guidance documents
- **Architecture:** RAG over ingested regulator guidance + internal compliance policies
- **Use cases:** "Do I need an AFSL for X?", "What's my deadline for Y?"
- **Guardrails:** Cites sources, flags uncertainty, escalates to human advisor

#### P2-F3: Regulatory Update Feed
- **Description:** AI-powered monitoring of regulator announcements
- **Sources:** ASIC media releases, AUSTRAC bulletins, APRA updates, DTA policy
- **Risk adjustment:** Automatically assesses impact on each customer's compliance profile
- **Delivery:** In-app feed + weekly email digest

#### P2-F4: Fair Trading / Consumer Protection Checklists
- **Description:** Jurisdiction-specific fair trading compliance
- **States:** NSW, VIC, QLD, WA, SA, ACT, TAS, NT
- **Topics:** Advertising, refunds, warranties, cooling-off periods, dispute resolution

#### P2-F5: Compliance Score Dashboard
- **Description:** 0-100 compliance health score per regulation domain
- **Factors:** Completed actions, overdue items, risk exposure, audit readiness
- **Visualisation:** Traffic light dashboard (Green/Amber/Red)
- **Trending:** Week-over-week and month-over-month changes

#### P2-F6: Evidence Pack Generator
- **Description:** Board-ready compliance evidence packs
- **Scope:** Per regulation or consolidated multi-regulation
- **Format:** PDF with cover sheet, executive summary, evidence appendix
- **Template:** Matches ASIC 12-point framework (BoardProof compatibility)

### PHASE 3: Platform + Partners (Months 7-12)

#### P3-F1: API for Vertical SaaS Partners
- **Description:** Embeddable compliance widgets for property management, accounting, legal practice software
- **Endpoints:** Compliance assessment, deadline check, form generation, risk scoring
- **Pricing:** Per-assessment or per-seat with partner margin
- **Target:** Xero Add-on, MYOB Marketplace, property management platforms

#### P3-F2: White-Label for Industry Associations
- **Description:** Custom-branded compliance portals for industry bodies
- **Targets:** REI (Real Estate Institute), Legal associations, Accounting bodies
- **Features:** Association branding, member pricing, reporting to association

#### P3-F3: PayTo Compliance Module
- **Description:** New Payments Platform (NPP) compliance workflows
- **Requirements:** Mandatory from 2027 for certain payment types
- **Features:** Consent management, mandate tracking, dispute handling

#### P3-F4: Insurance Distribution Module
- **Description:** Insurance compliance under the Insurance Contracts Act
- **Features:** Disclosure documents, duty of disclosure, claims handling, complaints
- **Target:** Insurance brokers, intermediaries, comparison sites

#### P3-F5: Privacy Act Compliance
- **Description:** Australian Privacy Principles (APP) compliance workflows
- **Features:** Privacy policy generator, breach notification, data request handling, consent management
- **Timing:** Aligns with Privacy Act reform (expected 2026-27)

#### P3-F6: Cross-Jurisdiction Compliance
- **Description:** Dual AU-EU, AU-UK compliance for fintechs
- **Features:** EU AI Act overlay, GDPR mapping to APP, UK FCA equivalence
- **Target:** AU fintechs expanding internationally

---

## Feature Prioritisation Matrix

| ID | Feature | Phase | Effort | Impact | Urgency | Priority |
|:---|:--------|:------|:-------|:-------|:--------|:---------|
| P1-F2 | AML CDD Workflow Builder | 1 | Medium | High | Critical | 🏆 P0 |
| P1-F3 | AUSTRAC Reporting | 1 | Medium | High | Critical | 🏆 P0 |
| P1-F1 | Business Profile Wizard | 1 | Low | High | High | P1 |
| P1-F4 | Document Upload & Verification | 1 | Medium | High | High | P1 |
| P1-F5 | Risk Scoring Matrix | 1 | Low | Medium | High | P1 |
| P1-F6 | Audit Trail Storage | 1 | Low | High | High | P1 |
| P1-F7 | Compliance Calendar | 1 | Low | Medium | Medium | P2 |
| P1-F8 | Team & Role Management | 1 | Medium | Medium | Medium | P2 |
| P2-F1 | BNPL Licensing Workflow | 2 | Medium | High | Medium | P1 |
| P2-F2 | AI Compliance Advisor | 2 | High | High | Medium | P1 |
| P2-F3 | Regulatory Update Feed | 2 | Medium | Medium | Medium | P2 |
| P2-F5 | Compliance Score Dashboard | 2 | Medium | High | Low | P2 |
| P2-F6 | Evidence Pack Generator | 2 | Medium | High | Low | P2 |
| P3-F1 | API for Partners | 3 | High | High | Low | P1 |
| P3-F2 | White-Label | 3 | Medium | Medium | Low | P2 |
| P3-F3–6 | Vertical Modules | 3 | Varies | Medium | Low | P3 |

---

## Key Design Decisions

1. **Form → Engine → Output** — same pipeline for all regulations, just swap rulesets
2. **No-code workflow builder** — SMEs cannot afford developers; wizards must be drag-and-drop or form-based
3. **API-first** — Phase 1 is a web app, but architecture must support embedded widgets in partners' products
4. **Offline-capable** — Some regulated SMEs operate in areas with limited connectivity; form filling should work offline
5. **Audit-ready by default** — Every action must be logged with timestamp and user identity
6. **Regulation-as-config** — Adding a new regulation should be a config change, not a code change

## Integration Points

| System | Type | Purpose |
|--------|------|---------|
| GreenID | API | Identity verification |
| AUSTRAC | API/Upload | Report submission |
| Xero/MYOB | API | Pull transaction data for AML monitoring |
| ASIC registers | API | Director/company lookups |
| ABR | API | ABN/entity validation |
| Email (IMAP) | Integration | Ingest regulator announcements |
