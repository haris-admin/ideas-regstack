# RegStack — Python Prototype (FastAPI Backend + Frontend)
# Compliance Risk Scoring Engine + CDD Workflow
# Phase: Weekend MVP

import json
from enum import Enum
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

# ============================================================
# PHASE 1: DATA MODELS
# ============================================================

class Industry(str, Enum):
    real_estate = "real_estate"
    legal = "legal"
    accounting = "accounting"
    fintech = "fintech"
    insurance = "insurance"
    remittance = "remittance"
    gambling = "gambling"
    other = "other"

class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class CustomerType(str, Enum):
    individual = "individual"
    company = "company"
    trust = "trust"
    partnership = "partnership"

class IDType(str, Enum):
    passport = "passport"
    drivers_license = "drivers_license"
    birth_certificate = "birth_certificate"
    company_extract = "company_extract"

class BusinessProfile(BaseModel):
    business_name: str
    abn: str
    industry: Industry
    services_offered: list[str]
    estimated_monthly_transactions: int
    states_operating_in: list[str]
    has_compliance_officer: bool = False
    current_compliance_tools: str = "spreadsheets"

class CDDRecord(BaseModel):
    customer_name: str
    customer_type: CustomerType
    date_of_birth: Optional[date] = None
    address: str
    id_type: IDType
    id_number: str
    id_expiry: Optional[date] = None
    transaction_purpose: str
    source_of_funds: str
    country_of_residence: str = "Australia"
    politically_exposed: bool = False
    adverse_media: bool = False

class RiskAssessment(BaseModel):
    cdd: CDDRecord
    industry_risk: RiskLevel
    jurisdiction_risk: RiskLevel
    transaction_risk: RiskLevel
    overall_risk: RiskLevel
    score: int
    factors: list[str]

# ============================================================
# PHASE 2: RISK SCORING ENGINE
# ============================================================

class RiskScoringEngine:
    """Configurable risk scoring matrix for AML/CDD compliance."""

    INDUSTRY_RISK_MAP = {
        Industry.real_estate: RiskLevel.medium,
        Industry.legal: RiskLevel.high,
        Industry.accounting: RiskLevel.high,
        Industry.fintech: RiskLevel.high,
        Industry.insurance: RiskLevel.medium,
        Industry.remittance: RiskLevel.high,
        Industry.gambling: RiskLevel.high,
        Industry.other: RiskLevel.low,
    }

    HIGH_RISK_JURISDICTIONS = [
        "Iran", "North Korea", "Myanmar", "Syria", "Yemen",
        "Russia", "Belarus",
    ]

    def score_industry(self, industry: Industry) -> tuple[RiskLevel, int]:
        risk = self.INDUSTRY_RISK_MAP.get(industry, RiskLevel.low)
        scores = {RiskLevel.low: 10, RiskLevel.medium: 30, RiskLevel.high: 50}
        return risk, scores[risk]

    def score_jurisdiction(self, country: str) -> tuple[RiskLevel, int]:
        if country in self.HIGH_RISK_JURISDICTIONS:
            return RiskLevel.high, 50
        if country != "Australia":
            return RiskLevel.medium, 20
        return RiskLevel.low, 10

    def score_transaction_volume(self, est_monthly: int) -> tuple[RiskLevel, int]:
        if est_monthly > 1000:
            return RiskLevel.high, 40
        if est_monthly > 100:
            return RiskLevel.medium, 20
        return RiskLevel.low, 10

    def score_customer_flags(self, cdd: CDDRecord) -> tuple[RiskLevel, int, list[str]]:
        score = 0
        factors = []
        if cdd.politically_exposed:
            score += 30
            factors.append("Politically exposed person")
        if cdd.adverse_media:
            score += 40
            factors.append("Adverse media match")
        if cdd.transaction_purpose.lower() in ["cash business", "money service"]:
            score += 15
            factors.append("High-risk transaction purpose")
        risk = RiskLevel.low
        if score >= 50:
            risk = RiskLevel.high
        elif score >= 20:
            risk = RiskLevel.medium
        return risk, score, factors

    def assess(self, cdd: CDDRecord, industry: Industry, est_monthly: int) -> RiskAssessment:
        ind_risk, ind_score = self.score_industry(industry)
        jur_risk, jur_score = self.score_jurisdiction(cdd.country_of_residence)
        tx_risk, tx_score = self.score_transaction_volume(est_monthly)
        cus_risk, cus_score, cus_factors = self.score_customer_flags(cdd)

        total = ind_score + jur_score + tx_score + cus_score
        factors = cus_factors[:]

        if ind_score > 30:
            factors.append(f"Industry: {industry.value}")
        if jur_score > 20:
            factors.append(f"Jurisdiction: {cdd.country_of_residence}")

        if total >= 100:
            overall = RiskLevel.high
        elif total >= 50:
            overall = RiskLevel.medium
        else:
            overall = RiskLevel.low

        return RiskAssessment(
            cdd=cdd,
            industry_risk=ind_risk,
            jurisdiction_risk=jur_risk,
            transaction_risk=tx_risk,
            overall_risk=overall,
            score=total,
            factors=factors,
        )

# ============================================================
# PHASE 3: COMPLIANCE FORM GENERATOR
# ============================================================

class FormGenerator:
    """Generates AUSTRAC-ready compliance forms."""

    def generate_smr_form(self, assessment: RiskAssessment, organisation: str) -> dict:
        """Suspicious Matter Report form data."""
        return {
            "form_type": "SMR",
            "organisation": organisation,
            "generated_at": datetime.now().isoformat(),
            "customer": assessment.cdd.customer_name,
            "risk_level": assessment.overall_risk.value,
            "risk_score": assessment.score,
            "factors": assessment.factors,
            "based_on": "AUSTRAC AML/CTF Rules 2007",
            "status": "draft",
        }

    def generate_compliance_report(self, business: BusinessProfile, assessments: list[RiskAssessment]) -> str:
        """Generate a text compliance report."""
        lines = [
            "=" * 60,
            f"REGSTACK COMPLIANCE REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} AEST",
            f"Organisation: {business.business_name} (ABN: {business.abn})",
            f"Industry: {business.industry.value}",
            "=" * 60,
            "",
            "RISK SUMMARY",
            "-" * 40,
            f"Customer assessments completed: {len(assessments)}",
        ]

        if assessments:
            total_score = sum(a.score for a in assessments)
            avg_score = total_score / len(assessments)
            high_risk_count = sum(1 for a in assessments if a.overall_risk == RiskLevel.high)
            lines.append(f"Average risk score: {avg_score:.0f}/200")
            lines.append(f"High-risk customers: {high_risk_count}")
            lines.append("")

            for a in assessments:
                lines.append(f"  Customer: {a.cdd.customer_name}")
                lines.append(f"  Risk Level: {a.overall_risk.value.upper()} (Score: {a.score})")
                if a.factors:
                    lines.append(f"  Factors: {', '.join(a.factors)}")
                lines.append("")

        lines.extend([
            "DEADLINES",
            "-" * 40,
            "AUSTRAC Tranche 2: 1 July 2026",
            "Next report due: 30 days from today",
            "",
            "STATUS: DRAFT — Not filed with AUSTRAC",
            "=" * 60,
        ])
        return "\n".join(lines)

# ============================================================
# PHASE 4: FASTAPI SERVER
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="RegStack API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RiskScoringEngine()
form_gen = FormGenerator()

# In-memory store (MVP only — replace with PostgreSQL)
customers: list[CDDRecord] = []
assessments: list[RiskAssessment] = []
business_profiles: dict[str, BusinessProfile] = {}

@app.post("/api/business/profile")
def create_profile(profile: BusinessProfile):
    business_profiles[profile.abn] = profile
    return {"status": "ok", "abn": profile.abn}

@app.get("/api/business/{abn}")
def get_profile(abn: str):
    if abn not in business_profiles:
        raise HTTPException(404, "Business not found")
    return business_profiles[abn]

@app.post("/api/cdd/assess")
def assess_customer(cdd: CDDRecord, industry: Industry = Industry.real_estate, monthly_tx: int = 50):
    assessment = engine.assess(cdd, industry, monthly_tx)
    customers.append(cdd)
    assessments.append(assessment)
    return {
        "overall_risk": assessment.overall_risk.value,
        "score": assessment.score,
        "factors": assessment.factors,
        "breakdown": {
            "industry": assessment.industry_risk.value,
            "jurisdiction": assessment.jurisdiction_risk.value,
            "transaction": assessment.transaction_risk.value,
        }
    }

@app.get("/api/report/smr/{customer_idx}")
def generate_smr(customer_idx: int):
    if customer_idx >= len(assessments):
        raise HTTPException(404, "Assessment not found")
    return form_gen.generate_smr_form(
        assessments[customer_idx],
        list(business_profiles.keys())[0] if business_profiles else "Unknown",
    )

@app.get("/api/report/compliance")
def generate_compliance_report():
    business = next(iter(business_profiles.values())) if business_profiles else None
    if not business:
        return {"error": "No business profile found. Create one first."}
    report = form_gen.generate_compliance_report(business, assessments)
    return {"report": report}

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "customers_assessed": len(assessments),
        "deadline": "2026-07-01 (AUSTRAC Tranche 2)",
    }

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>RegStack — Compliance Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #f0f4f8; color: #1a202c; line-height: 1.6; }
        .header { background: linear-gradient(135deg, #1a365d, #2b6cb0);
                  color: white; padding: 2rem; text-align: center; }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.85; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 12px; padding: 1.5rem;
                margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { color: #2b6cb0; margin-bottom: 1rem; }
        .card.status { border-left: 4px solid #48bb78; }
        .card.alert { border-left: 4px solid #ed8936; }
        label { display: block; margin-top: 0.75rem; font-weight: 600; font-size: 0.9rem; color: #4a5568; }
        input, select, textarea { width: 100%; padding: 0.6rem; margin-top: 0.25rem;
                border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.95rem; }
        button { background: #2b6cb0; color: white; border: none; padding: 0.75rem 1.5rem;
                 border-radius: 8px; font-size: 1rem; margin-top: 1rem; cursor: pointer; }
        button:hover { background: #1a365d; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px;
                 font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
        .badge.low { background: #c6f6d5; color: #22543d; }
        .badge.medium { background: #fefcbf; color: #744210; }
        .badge.high { background: #fed7d7; color: #822727; }
        .result { margin-top: 1rem; padding: 1rem; background: #f7fafc; border-radius: 8px; }
        pre { background: #1a202c; color: #e2e8f0; padding: 1rem; border-radius: 8px;
              overflow-x: auto; font-size: 0.85rem; margin-top: 1rem; }
        .footer { text-align: center; padding: 2rem; color: #718096; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ RegStack</h1>
        <p>Multi-Regulation SME Compliance Platform — Weekend MVP</p>
    </div>
    <div class="container">
        <div class="card status">
            <h2>📊 System Status</h2>
            <p>Status: <strong>Running</strong></p>
            <p>Deadline: <strong>AUSTRAC Tranche 2 — 1 July 2026</strong> (32 days)</p>
            <p>Risk Engine: <strong>Active</strong></p>
        </div>

        <div class="card">
            <h2>📝 Customer Due Diligence</h2>
            <form id="cddForm">
                <label>Customer Name</label>
                <input name="customer_name" value="Jane Smith" required>
                <label>Customer Type</label>
                <select name="customer_type">
                    <option value="individual">Individual</option>
                    <option value="company">Company</option>
                    <option value="trust">Trust</option>
                </select>
                <label>ID Type</label>
                <select name="id_type">
                    <option value="passport">Passport</option>
                    <option value="drivers_license">Driver's License</option>
                    <option value="company_extract">Company Extract</option>
                </select>
                <label>Transaction Purpose</label>
                <input name="transaction_purpose" value="Property purchase">
                <label>Country of Residence</label>
                <input name="country_of_residence" value="Australia">
                <label>Industry</label>
                <select name="industry">
                    <option value="real_estate">Real Estate</option>
                    <option value="legal">Legal</option>
                    <option value="accounting">Accounting</option>
                    <option value="fintech">Fintech</option>
                </select>
                <label>
                    <input type="checkbox" name="politically_exposed"> Politically Exposed Person
                </label>
                <label>
                    <input type="checkbox" name="adverse_media"> Adverse Media Match
                </label>
                <button type="submit">Assess Risk</button>
            </form>
            <div id="result" class="result" style="display:none;"></div>
        </div>

        <div class="card alert">
            <h2>⚠️ AUSTRAC Tranche 2 Countdown</h2>
            <p style="font-size:2rem;font-weight:700;" id="countdown">32 days</p>
            <p>Real estate agents, lawyers, and accountants must be compliant.</p>
        </div>

        <div class="card">
            <h2>📄 Compliance Report</h2>
            <button onclick="generateReport()">Generate Report</button>
            <pre id="reportOutput" style="margin-top:1rem;"></pre>
        </div>
    </div>
    <div class="footer">RegStack v0.1.0 — Powered by Python / FastAPI</div>

    <script>
        document.getElementById('cddForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = Object.fromEntries(new FormData(e.target));
            data.politically_exposed = !!data.politically_exposed;
            data.adverse_media = !!data.adverse_media;
            const params = new URLSearchParams({ industry: data.industry, monthly_tx: '50' });
            delete data.industry;
            const res = await fetch('/api/cdd/assess?' + params, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            const result = await res.json();
            document.getElementById('result').style.display = 'block';
            document.getElementById('result').innerHTML =
                '<p><span class="badge ' + result.overall_risk + '">' + result.overall_risk.toUpperCase() + '</span>' +
                ' Risk Score: <strong>' + result.score + '/200</strong></p>' +
                '<p>Factors: ' + (result.factors.length ? result.factors.join(', ') : 'None') + '</p>';
        };

        async function generateReport() {
            const res = await fetch('/api/report/compliance');
            const data = await res.json();
            document.getElementById('reportOutput').textContent = data.report || data.error;
        }
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
