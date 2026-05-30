"""
RegStack — Supabase Client

Usage:
    from db.supabase.client import get_supabase
    supabase = get_supabase()

    # List organisations
    orgs = supabase.table("organisations").select("*").execute()
"""

import os
from typing import Optional
from supabase import create_client, Client


_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    global _client
    if _client is not None:
        return _client

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment.\n"
            "Copy .env.example to .env.local and fill in your Supabase credentials."
        )

    _client = create_client(url, key)
    return _client


class RegStackDB:
    """High-level database operations for RegStack."""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()

    # ── Organisation ──

    def create_organisation(self, business_name: str, abn: str, industry_sector: str, **kwargs) -> dict:
        data = {"business_name": business_name, "abn": abn, "industry_sector": industry_sector, **kwargs}
        result = self.client.table("organisations").insert(data).execute()
        return result.data[0] if result.data else {}

    def get_organisation(self, org_id: str) -> Optional[dict]:
        result = self.client.table("organisations").select("*").eq("id", org_id).execute()
        return result.data[0] if result.data else None

    def list_organisations(self, status: str = "active") -> list:
        result = self.client.table("organisations").select("*").eq("status", status).execute()
        return result.data

    # ── CDD Records ──

    def create_cdd_record(self, org_id: str, customer_name: str, **kwargs) -> dict:
        data = {"org_id": org_id, "customer_name": customer_name, **kwargs}
        result = self.client.table("cdd_records").insert(data).execute()
        return result.data[0] if result.data else {}

    def assess_cdd_risk(self, cdd_id: str, risk_level: str, risk_score: int, factors: list[str]) -> dict:
        data = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "assessment_factors": factors,
            "assessed_by": "system",
            "assessed_at": "now()",
        }
        result = self.client.table("cdd_records").update(data).eq("id", cdd_id).execute()
        return result.data[0] if result.data else {}

    def list_cdd_by_org(self, org_id: str) -> list:
        result = self.client.table("cdd_records").select("*").eq("org_id", org_id).execute()
        return result.data

    # ── Deadlines ──

    def get_upcoming_deadlines(self, org_id: str, limit: int = 20) -> list:
        result = (
            self.client.table("deadlines")
            .select("*")
            .eq("org_id", org_id)
            .eq("status", "pending")
            .order("due_date", desc=False)
            .limit(limit)
            .execute()
        )
        return result.data

    def get_overdue_deadlines(self, org_id: str) -> list:
        result = (
            self.client.table("deadlines")
            .select("*")
            .eq("org_id", org_id)
            .eq("status", "pending")
            .lt("due_date", "CURRENT_DATE")
            .order("due_date", desc=False)
            .execute()
        )
        return result.data

    # ── Submissions ──

    def create_submission(self, org_id: str, submission_type: str, regulator: str, **kwargs) -> dict:
        data = {"org_id": org_id, "submission_type": submission_type, "regulator": regulator, **kwargs}
        result = self.client.table("submissions").insert(data).execute()
        return result.data[0] if result.data else {}

    # ── Audit Trail ──

    def log_action(self, org_id: str, action: str, actor: str, description: str, **kwargs) -> dict:
        data = {"org_id": org_id, "action": action, "actor": actor, "description": description, **kwargs}
        result = self.client.table("audit_trail").insert(data).execute()
        return result.data[0] if result.data else {}

    # ── Reports ──

    def get_compliance_summary(self, org_id: str) -> dict:
        """Summary of compliance status for an organisation."""
        total = self.client.table("assessments").select("*", count="exact").eq("org_id", org_id).execute()
        compliant = self.client.table("assessments").select("*", count="exact").eq("org_id", org_id).eq("status", "compliant").execute()
        overdue = self.get_overdue_deadlines(org_id)

        return {
            "org_id": org_id,
            "total_assessments": len(total.data) if hasattr(total, 'data') else 0,
            "compliant": len(compliant.data) if hasattr(compliant, 'data') else 0,
            "overdue_deadlines": len(overdue),
            "status": "healthy" if len(overdue) == 0 else "attention_needed",
        }
