#!/usr/bin/env python3
"""
RegStack — Database Migration Script

Sets up the regulatory compliance database schema on any machine.
Supports SQLite (dev default) and PostgreSQL (production).

Usage:
    python db/migrate.py                          # SQLite dev database (./regstack.db)
    python db/migrate.py --to-pg                  # PostgreSQL via DATABASE_URL env var
    python db/migrate.py --to-pg --url=postgresql://user:pass@host:5432/regstack
    python db/migrate.py --verify                 # Verify schema only
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

# ─── Schema (from schema.sql) ───────────────────────────────────────────────

SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS regulations (
    id TEXT PRIMARY KEY,
    regulation_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    jurisdiction TEXT NOT NULL,
    category TEXT NOT NULL,
    regulation_body TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    sunset_date TEXT,
    risk_level TEXT NOT NULL DEFAULT 'medium',
    requires_submission INTEGER NOT NULL DEFAULT 0,
    submission_frequency TEXT,
    applicable_verticals TEXT,
    legislative_ref TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    entity_name TEXT NOT NULL,
    abn TEXT,
    acn TEXT,
    entity_type TEXT NOT NULL DEFAULT 'company',
    industry_sector TEXT,
    jurisdiction TEXT NOT NULL DEFAULT 'AU-FEDERAL',
    risk_rating TEXT DEFAULT 'medium',
    entity_status TEXT NOT NULL DEFAULT 'active',
    compliance_officer TEXT,
    email TEXT,
    phone TEXT,
    physical_address TEXT,
    mailing_address TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS assessments (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id TEXT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'not_assessed',
    score INTEGER CHECK (score >= 0 AND score <= 100),
    assessed_by TEXT,
    assessment_date TEXT NOT NULL DEFAULT (date('now')),
    next_review_date TEXT,
    findings TEXT,
    remediation_notes TEXT,
    evidence_links TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE (entity_id, regulation_id, assessment_date)
);

CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id TEXT REFERENCES regulations(id) ON DELETE SET NULL,
    submission_type TEXT NOT NULL,
    submission_reference TEXT,
    regulator TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    submitted_at TEXT,
    due_date TEXT,
    filed_by TEXT,
    submission_data TEXT DEFAULT '{}',
    response_data TEXT,
    notes TEXT,
    attachment_paths TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_trail (
    id TEXT PRIMARY KEY,
    entity_id TEXT REFERENCES entities(id) ON DELETE SET NULL,
    regulation_id TEXT REFERENCES regulations(id) ON DELETE SET NULL,
    assessment_id TEXT REFERENCES assessments(id) ON DELETE SET NULL,
    submission_id TEXT REFERENCES submissions(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    actor_role TEXT,
    changes TEXT DEFAULT '{}',
    ip_address TEXT,
    user_agent TEXT,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS deadlines (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id TEXT REFERENCES regulations(id) ON DELETE SET NULL,
    assessment_id TEXT REFERENCES assessments(id) ON DELETE SET NULL,
    submission_id TEXT REFERENCES submissions(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    deadline_type TEXT NOT NULL DEFAULT 'filing',
    due_date TEXT NOT NULL,
    reminder_date TEXT,
    reminder_sent INTEGER NOT NULL DEFAULT 0,
    reminder_sent_at TEXT,
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'pending',
    completed_at TEXT,
    assigned_to TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_regulations_jurisdiction ON regulations(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_regulations_category ON regulations(category);
CREATE INDEX IF NOT EXISTS idx_regulations_effective_date ON regulations(effective_date);
CREATE INDEX IF NOT EXISTS idx_regulations_body ON regulations(regulation_body);
CREATE INDEX IF NOT EXISTS idx_entities_abn ON entities(abn);
CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(entity_status);
CREATE INDEX IF NOT EXISTS idx_entities_sector ON entities(industry_sector);
CREATE INDEX IF NOT EXISTS idx_entities_risk ON entities(risk_rating);
CREATE INDEX IF NOT EXISTS idx_assessments_entity ON assessments(entity_id);
CREATE INDEX IF NOT EXISTS idx_assessments_regulation ON assessments(regulation_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessments_next_review ON assessments(next_review_date);
CREATE INDEX IF NOT EXISTS idx_assessments_composite ON assessments(entity_id, regulation_id);
CREATE INDEX IF NOT EXISTS idx_submissions_entity ON submissions(entity_id);
CREATE INDEX IF NOT EXISTS idx_submissions_regulator ON submissions(regulator);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_due ON submissions(due_date);
CREATE INDEX IF NOT EXISTS idx_submissions_type ON submissions(submission_type);
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity ON audit_trail(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_action ON audit_trail(action);
CREATE INDEX IF NOT EXISTS idx_audit_trail_actor ON audit_trail(actor);
CREATE INDEX IF NOT EXISTS idx_audit_trail_created ON audit_trail(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_trail_assessment ON audit_trail(assessment_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_entity ON deadlines(entity_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_due_date ON deadlines(due_date);
CREATE INDEX IF NOT EXISTS idx_deadlines_status ON deadlines(status);
CREATE INDEX IF NOT EXISTS idx_deadlines_priority ON deadlines(priority);
CREATE INDEX IF NOT EXISTS idx_deadlines_reminder ON deadlines(reminder_date, reminder_sent);
"""

SCHEMA_POSTGRES = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS regulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation_code VARCHAR(50) NOT NULL UNIQUE,
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
    applicable_verticals TEXT[],
    legislative_ref TEXT,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name VARCHAR(200) NOT NULL,
    abn VARCHAR(11),
    acn VARCHAR(9),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'company',
    industry_sector VARCHAR(100),
    jurisdiction VARCHAR(50) NOT NULL DEFAULT 'AU-FEDERAL',
    risk_rating VARCHAR(20) DEFAULT 'medium',
    entity_status VARCHAR(30) NOT NULL DEFAULT 'active',
    compliance_officer VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(50),
    physical_address TEXT,
    mailing_address TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id UUID NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
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
    UNIQUE (entity_id, regulation_id, assessment_date)
);

CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
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
    attachment_paths TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES entities(id) ON DELETE SET NULL,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
    assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(200) NOT NULL,
    actor_role VARCHAR(50),
    changes JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deadlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    regulation_id UUID REFERENCES regulations(id) ON DELETE SET NULL,
    assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline_type VARCHAR(50) NOT NULL DEFAULT 'filing',
    due_date DATE NOT NULL,
    reminder_date DATE,
    reminder_sent BOOLEAN NOT NULL DEFAULT false,
    reminder_sent_at TIMESTAMPTZ,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    completed_at TIMESTAMPTZ,
    assigned_to VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_regulations_jurisdiction ON regulations(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_regulations_category ON regulations(category);
CREATE INDEX IF NOT EXISTS idx_regulations_effective_date ON regulations(effective_date);
CREATE INDEX IF NOT EXISTS idx_regulations_body ON regulations(regulation_body);
CREATE INDEX IF NOT EXISTS idx_entities_abn ON entities(abn);
CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(entity_status);
CREATE INDEX IF NOT EXISTS idx_entities_sector ON entities(industry_sector);
CREATE INDEX IF NOT EXISTS idx_entities_risk ON entities(risk_rating);
CREATE INDEX IF NOT EXISTS idx_assessments_entity ON assessments(entity_id);
CREATE INDEX IF NOT EXISTS idx_assessments_regulation ON assessments(regulation_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessments_next_review ON assessments(next_review_date);
CREATE INDEX IF NOT EXISTS idx_assessments_composite ON assessments(entity_id, regulation_id);
CREATE INDEX IF NOT EXISTS idx_submissions_entity ON submissions(entity_id);
CREATE INDEX IF NOT EXISTS idx_submissions_regulator ON submissions(regulator);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_due ON submissions(due_date);
CREATE INDEX IF NOT EXISTS idx_submissions_type ON submissions(submission_type);
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity ON audit_trail(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_action ON audit_trail(action);
CREATE INDEX IF NOT EXISTS idx_audit_trail_actor ON audit_trail(actor);
CREATE INDEX IF NOT EXISTS idx_audit_trail_created ON audit_trail(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_trail_assessment ON audit_trail(assessment_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_entity ON deadlines(entity_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_due_date ON deadlines(due_date);
CREATE INDEX IF NOT EXISTS idx_deadlines_status ON deadlines(status);
CREATE INDEX IF NOT EXISTS idx_deadlines_priority ON deadlines(priority);
CREATE INDEX IF NOT EXISTS idx_deadlines_reminder ON deadlines(reminder_date, reminder_sent)
    WHERE reminder_sent = false;
"""

# ─── Migration Engine ───────────────────────────────────────────────────────

def migrate_sqlite(db_path: str) -> dict:
    """Run SQLite migration. Returns stats."""
    conn = sqlite3.connect(db_path)
    conn.executescript("PRAGMA journal_mode=WAL;")
    conn.executescript(SCHEMA_SQLITE)
    conn.commit()

    # Verify
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()

    return {
        "status": "ok",
        "engine": "sqlite",
        "path": os.path.abspath(db_path),
        "tables": tables,
    }


def migrate_postgres(conn_str: str) -> dict:
    """Run PostgreSQL migration. Returns stats."""
    try:
        import psycopg2
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute(SCHEMA_POSTGRES)
        conn.commit()

        # Verify
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' ORDER BY table_name"
        )
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {
            "status": "ok",
            "engine": "postgresql",
            "connection": conn_str,
            "tables": tables,
        }
    except ImportError:
        return {"status": "error", "message": "psycopg2 not installed. Run: pip install psycopg2-binary"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def verify_sqlite(db_path: str) -> dict:
    """Verify SQLite schema is complete."""
    expected = {"regulations", "entities", "assessments", "submissions", "audit_trail", "deadlines"}
    conn = sqlite3.connect(db_path)
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    found = {row[0] for row in cur.fetchall()}
    conn.close()
    missing = expected - found
    return {
        "db_path": db_path,
        "tables_found": sorted(found),
        "missing": sorted(missing),
        "complete": len(missing) == 0,
    }


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RegStack — Database Migration")
    parser.add_argument("--to-pg", action="store_true", help="Use PostgreSQL instead of SQLite")
    parser.add_argument("--url", help="Database URL (overrides DATABASE_URL env)")
    parser.add_argument("--db-path", default="./regstack.db", help="SQLite database file path")
    parser.add_argument("--verify", action="store_true", help="Verify schema only")
    args = parser.parse_args()

    db_url = args.url or os.getenv("DATABASE_URL")

    if args.verify:
        if args.to_pg or db_url:
            print(json.dumps({"error": "Verify mode only supports SQLite"}, indent=2))
            sys.exit(1)
        result = verify_sqlite(args.db_path)
        print(json.dumps(result, indent=2))
        if not result["complete"]:
            print(f"\n❌ Missing tables: {', '.join(result['missing'])}")
            print("   Run: python db/migrate.py")
            sys.exit(1)
        print("✅ Schema verified — all tables present")
        return

    if args.to_pg or db_url:
        conn_str = db_url or os.getenv("DATABASE_URL", "postgresql://regstack:regstack@localhost:5432/regstack")
        print(f"🌐 Connecting to PostgreSQL: {conn_str}")
        result = migrate_postgres(conn_str)
    else:
        print(f"🗄️  Creating SQLite database: {args.db_path}")
        result = migrate_sqlite(args.db_path)

    print(json.dumps(result, indent=2))

    if result.get("status") == "ok":
        print(f"\n✅ Migration complete — {len(result.get('tables', []))} tables created")
    else:
        print(f"\n❌ Migration failed: {result.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
