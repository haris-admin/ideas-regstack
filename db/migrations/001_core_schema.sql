-- RegStack — Migration 001: Core Schema
-- Target: Supabase (PostgreSQL 15+)
-- Run: psql or Supabase SQL Editor
--
-- RegStack: Multi-Regulation SME Compliance Platform
-- Tech stack: Python backend / Supabase / Next.js frontend / R2 storage

-- ── Extensions ──
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── 1. Organisation profiles ──
CREATE TABLE IF NOT EXISTS organisations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(200) NOT NULL,
    abn VARCHAR(11) UNIQUE,
    acn VARCHAR(9),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'company',
    industry_sector VARCHAR(100),
    jurisdiction VARCHAR(50) NOT NULL DEFAULT 'AU-FEDERAL',
    risk_rating VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    compliance_officer VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(50),
    physical_address TEXT,
    services_offered TEXT[],
    states_operating TEXT[],
    estimated_monthly_transactions INTEGER DEFAULT 0,
    has_compliance_officer BOOLEAN DEFAULT false,
    current_compliance_tools TEXT DEFAULT 'spreadsheets',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 2. Regulations catalog ──
CREATE TABLE IF NOT EXISTS regulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    jurisdiction VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    regulation_body VARCHAR(50) NOT NULL,
    effective_date DATE NOT NULL,
    sunset_date DATE,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    requires_submission BOOLEAN NOT NULL DEFAULT false,
    submission_frequency VARCHAR(30),
    applicable_industries TEXT[],
    legislative_ref TEXT,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 3. Customer due diligence records ──
CREATE TABLE IF NOT EXISTS cdd_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(30) NOT NULL DEFAULT 'individual',
    date_of_birth DATE,
    address TEXT,
    id_type VARCHAR(50),
    id_number VARCHAR(100),
    id_expiry DATE,
    transaction_purpose TEXT,
    source_of_funds TEXT,
    country_of_residence VARCHAR(100) DEFAULT 'Australia',
    politically_exposed BOOLEAN DEFAULT false,
    adverse_media BOOLEAN DEFAULT false,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'not_assessed',
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 200),
    assessment_factors TEXT[],
    assessed_by VARCHAR(200),
    assessed_at TIMESTAMPTZ,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. Compliance assessments ──
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
    cdd_id UUID REFERENCES cdd_records(id) ON DELETE SET NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'not_assessed',
    score INTEGER CHECK (score >= 0 AND score <= 100),
    assessed_by VARCHAR(200),
    assessment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    next_review_date DATE,
    findings TEXT,
    remediation_notes TEXT,
    evidence_links TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (org_id, regulation_id, assessment_date)
);

-- ── 5. Regulatory submissions ──
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
    submission_type VARCHAR(50) NOT NULL,
    submission_reference VARCHAR(100),
    regulator VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    submitted_at TIMESTAMPTZ,
    due_date DATE,
    filed_by VARCHAR(200),
    submission_data JSONB DEFAULT '{}',
    response_data JSONB,
    notes TEXT,
    attachment_urls TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 6. Immutable audit trail ──
CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organisations(id) ON DELETE SET NULL,
    cdd_id UUID REFERENCES cdd_records(id) ON DELETE SET NULL,
    assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(200) NOT NULL,
    actor_role VARCHAR(50),
    changes JSONB DEFAULT '{}',
    description TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 7. Deadline calendar ──
CREATE TABLE IF NOT EXISTS deadlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline_type VARCHAR(50) NOT NULL DEFAULT 'filing',
    due_date DATE NOT NULL,
    reminder_date DATE,
    reminder_sent BOOLEAN NOT NULL DEFAULT false,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    completed_at TIMESTAMPTZ,
    assigned_to VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 8. Organisation users ──
CREATE TABLE IF NOT EXISTS org_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(200) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (org_id, email)
);

-- ── Indexes ──
CREATE INDEX IF NOT EXISTS idx_cdd_org ON cdd_records(org_id);
CREATE INDEX IF NOT EXISTS idx_cdd_risk ON cdd_records(risk_level);
CREATE INDEX IF NOT EXISTS idx_cdd_status ON cdd_records(status);
CREATE INDEX IF NOT EXISTS idx_assessments_org ON assessments(org_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessments_next_review ON assessments(next_review_date);
CREATE INDEX IF NOT EXISTS idx_submissions_org ON submissions(org_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_due ON submissions(due_date);
CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_trail(org_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_trail(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_deadlines_org ON deadlines(org_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_due ON deadlines(due_date);
CREATE INDEX IF NOT EXISTS idx_deadlines_reminder ON deadlines(reminder_date, reminder_sent)
    WHERE NOT reminder_sent;
CREATE INDEX IF NOT EXISTS idx_regulations_body ON regulations(regulation_body);
CREATE INDEX IF NOT EXISTS idx_regulations_effective ON regulations(effective_date);

-- ── Updated_at trigger ──
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT unnest(ARRAY['organisations', 'regulations', 'cdd_records', 'assessments', 'submissions', 'deadlines'])
    LOOP
        EXECUTE format('
            CREATE TRIGGER set_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at()', t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
