-- RegStack — Database Schema
-- PostgreSQL 16 compatible | Also works on SQLite (dev)
-- Run via: python db/migrate.py
--
-- Regulatory compliance stack for Australian businesses.
-- Targets: AML/CTF (AUSTRAC), Privacy (OAIC), AI Governance, etc.

-- ── Extension ──────────────────────────────────────────────────────────────
-- Included for pg; SQLite ignores unknown CREATE EXTENSION via inline checks.

-- ── Regulations ────────────────────────────────────────────────────────────
-- Core catalog of regulatory obligations an entity must comply with.
CREATE TABLE IF NOT EXISTS regulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation_code VARCHAR(50) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    jurisdiction VARCHAR(50) NOT NULL,
        -- e.g. 'AU-FEDERAL', 'AU-NSW', 'AU-VIC', 'AUSTRAC', 'OAIC'
    category VARCHAR(50) NOT NULL,
        -- e.g. 'AML_CTF', 'PRIVACY', 'AI_GOVERNANCE', 'CONSUMER_LAW', 'CORPORATE'
    regulation_body VARCHAR(50) NOT NULL,
        -- e.g. 'AUSTRAC', 'OAIC', 'ASIC', 'ATO', 'ACCC'
    effective_date DATE NOT NULL,
        -- When the regulation takes / took effect
    sunset_date DATE,
        -- When the regulation is repealed or superseded (nullable)
    risk_level VARCHAR(20) NOT NULL DEFAULT 'medium',
        -- 'low', 'medium', 'high', 'critical'
    requires_submission BOOLEAN NOT NULL DEFAULT false,
    submission_frequency VARCHAR(30),
        -- e.g. 'once', 'annual', 'quarterly', 'event_driven', 'continuous'
    applicable_verticals TEXT[],
        -- e.g. ARRAY['fintech', 'crypto', 'lending', 'real_estate', 'health']
    legislative_ref TEXT,
        -- Link or reference to the legislation instrument
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Entities ────────────────────────────────────────────────────────────────
-- Regulated entities (businesses, organisations) being tracked for compliance.
CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name VARCHAR(200) NOT NULL,
    abn VARCHAR(11),
        -- Australian Business Number (11 digits)
    acn VARCHAR(9),
        -- Australian Company Number (9 digits)
    entity_type VARCHAR(50) NOT NULL DEFAULT 'company',
        -- e.g. 'company', 'trust', 'sole_trader', 'partnership', 'charity'
    industry_sector VARCHAR(100),
        -- e.g. 'fintech', 'crypto_asset', 'banking', 'real_estate', 'legal'
    jurisdiction VARCHAR(50) NOT NULL DEFAULT 'AU-FEDERAL',
    risk_rating VARCHAR(20) DEFAULT 'medium',
        -- Overall entity risk rating: 'low', 'medium', 'high', 'critical'
    entity_status VARCHAR(30) NOT NULL DEFAULT 'active',
        -- 'active', 'pending_onboarding', 'suspended', 'decommissioned'
    compliance_officer VARCHAR(200),
        -- Name or contact of the designated compliance officer
    email VARCHAR(255),
    phone VARCHAR(50),
    physical_address TEXT,
    mailing_address TEXT,
    metadata JSONB DEFAULT '{}',
        -- Flexible extra attributes
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Assessments ─────────────────────────────────────────────────────────────
-- Compliance assessments: entity × regulation × current status.
-- Tracks whether an entity meets each applicable regulation.
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id UUID NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'not_assessed',
        -- 'not_assessed', 'compliant', 'partially_compliant',
        -- 'non_compliant', 'under_review', 'exempt'
    score INTEGER CHECK (score >= 0 AND score <= 100),
        -- Numerical compliance score (0-100), nullable
    assessed_by VARCHAR(200),
        -- Name or system identifier of the assessor
    assessment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    next_review_date DATE,
        -- Scheduled next review / reassessment date
    findings TEXT,
        -- Narrative of findings during the assessment
    remediation_notes TEXT,
        -- Actions required to achieve compliance
    evidence_links TEXT[],
        -- Array of URLs or file references to supporting evidence
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (entity_id, regulation_id, assessment_date)
        -- One assessment per entity-regulation per date
);

-- ── Submissions ─────────────────────────────────────────────────────────────
-- Regulatory submissions and filings (e.g., AUSTRAC reports, OAIC notifications).
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
        -- Optional link to the regulation that triggered the submission
    submission_type VARCHAR(50) NOT NULL,
        -- e.g. 'TTR' (Threshold Transaction Report),
        --      'SMR' (Suspicious Matter Report),
        --      'AML_CTF_COMPLIANCE_REPORT',
        --      'PRIVACY_BREACH_NOTIFICATION',
        --      'ANNUAL_RETURN'
    submission_reference VARCHAR(100),
        -- Reference ID from the regulator (if acknowledged)
    regulator VARCHAR(50) NOT NULL,
        -- e.g. 'AUSTRAC', 'OAIC', 'ASIC', 'ATO'
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
        -- 'draft', 'submitted', 'acknowledged', 'accepted', 'rejected', 'amended'
    submitted_at TIMESTAMPTZ,
        -- When the submission was actually sent
    due_date DATE,
        -- Filing deadline
    filed_by VARCHAR(200),
        -- Person or system that prepared/filed the submission
    submission_data JSONB DEFAULT '{}',
        -- Full payload of the submission for audit
    response_data JSONB,
        -- Regulator response / acknowledgement details
    notes TEXT,
    attachment_paths TEXT[],
        -- Paths or URLs to supporting documents
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Audit Trail ─────────────────────────────────────────────────────────────
-- Immutable log of all compliance-related actions for auditability.
CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES entities(id) ON DELETE SET NULL,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
    assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
        -- e.g. 'assessment_created', 'status_changed', 'submission_filed',
        --      'deadline_set', 'entity_onboarded', 'remediation_added'
    actor VARCHAR(200) NOT NULL,
        -- User or system that performed the action
    actor_role VARCHAR(50),
        -- e.g. 'compliance_officer', 'system', 'admin'
    changes JSONB DEFAULT '{}',
        -- Structured diff or before/after values
    ip_address VARCHAR(45),
        -- Client IP for traceability
    user_agent TEXT,
    description TEXT,
        -- Human-readable summary of what happened
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Deadlines ──────────────────────────────────────────────────────────────
-- Upcoming compliance deadlines, due dates, and reminders.
CREATE TABLE IF NOT EXISTS deadlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
    assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
        -- e.g. 'AUSTRAC AML/CTF Annual Report Due'
    description TEXT,
    deadline_type VARCHAR(50) NOT NULL DEFAULT 'filing',
        -- 'filing', 'assessment_review', 'remediation', 'renewal', 'general'
    due_date DATE NOT NULL,
    reminder_date DATE,
        -- When to send a reminder (before due_date)
    reminder_sent BOOLEAN NOT NULL DEFAULT false,
    reminder_sent_at TIMESTAMPTZ,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
        -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
        -- 'pending', 'completed', 'overdue', 'waived', 'cancelled'
    completed_at TIMESTAMPTZ,
    assigned_to VARCHAR(200),
        -- Person responsible for meeting this deadline
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ─────────────────────────────────────────────────────────────────

-- Regulations
CREATE INDEX IF NOT EXISTS idx_regulations_jurisdiction ON regulations(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_regulations_category ON regulations(category);
CREATE INDEX IF NOT EXISTS idx_regulations_effective_date ON regulations(effective_date);
CREATE INDEX IF NOT EXISTS idx_regulations_body ON regulations(regulation_body);

-- Entities
CREATE INDEX IF NOT EXISTS idx_entities_abn ON entities(abn);
CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(entity_status);
CREATE INDEX IF NOT EXISTS idx_entities_sector ON entities(industry_sector);
CREATE INDEX IF NOT EXISTS idx_entities_risk ON entities(risk_rating);

-- Assessments
CREATE INDEX IF NOT EXISTS idx_assessments_entity ON assessments(entity_id);
CREATE INDEX IF NOT EXISTS idx_assessments_regulation ON assessments(regulation_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessments_next_review ON assessments(next_review_date);
CREATE INDEX IF NOT EXISTS idx_assessments_composite ON assessments(entity_id, regulation_id);

-- Submissions
CREATE INDEX IF NOT EXISTS idx_submissions_entity ON submissions(entity_id);
CREATE INDEX IF NOT EXISTS idx_submissions_regulator ON submissions(regulator);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_due ON submissions(due_date);
CREATE INDEX IF NOT EXISTS idx_submissions_type ON submissions(submission_type);

-- Audit Trail
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity ON audit_trail(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_action ON audit_trail(action);
CREATE INDEX IF NOT EXISTS idx_audit_trail_actor ON audit_trail(actor);
CREATE INDEX IF NOT EXISTS idx_audit_trail_created ON audit_trail(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_trail_assessment ON audit_trail(assessment_id);

-- Deadlines
CREATE INDEX IF NOT EXISTS idx_deadlines_entity ON deadlines(entity_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_due_date ON deadlines(due_date);
CREATE INDEX IF NOT EXISTS idx_deadlines_status ON deadlines(status);
CREATE INDEX IF NOT EXISTS idx_deadlines_priority ON deadlines(priority);
CREATE INDEX IF NOT EXISTS idx_deadlines_reminder ON deadlines(reminder_date, reminder_sent)
    WHERE reminder_sent = false;
