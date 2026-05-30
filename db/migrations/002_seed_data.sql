-- RegStack — Migration 002: Seed Data
-- Target: Supabase (PostgreSQL 15+)
-- Run AFTER 001_core_schema.sql

-- ── Seed Regulations ──
INSERT INTO regulations (code, title, description, jurisdiction, category, regulation_body, effective_date, risk_level, requires_submission, submission_frequency, applicable_industries, legislative_ref) VALUES
('AML-CTF-2007', 'Anti-Money Laundering and Counter-Terrorism Financing Act 2007',
 'Core AML/CTF obligations for reporting entities including customer due diligence, reporting, and record-keeping.',
 'AU-FEDERAL', 'AML_CTF', 'AUSTRAC', '2007-12-12', 'high', true, 'annual',
 ARRAY['fintech','real_estate','legal','accounting','gambling','remittance'],
 'https://www.austrac.gov.au/aml-ctf-act'),

('AML-TRANCHE-2-2026', 'AUSTRAC Tranche 2 — Real Estate, Legal, Accounting',
 'Extension of AML/CTF obligations to real estate agents, lawyers, and accountants. Effective 1 July 2026.',
 'AU-FEDERAL', 'AML_CTF', 'AUSTRAC', '2026-07-01', 'critical', true, 'annual',
 ARRAY['real_estate','legal','accounting'],
 'https://www.austrac.gov.au/tranche-2'),

('ASIC-DIGITAL-ASSETS-2026', 'ASIC Digital Assets Reporting',
 'Reporting requirements for digital asset service providers including crypto exchanges and BNPL lenders.',
 'AU-FEDERAL', 'CONSUMER_LAW', 'ASIC', '2026-06-30', 'high', true, 'quarterly',
 ARRAY['fintech','crypto'],
 'https://asic.gov.au/digital-assets'),

('PRIVACY-ACT-1988', 'Privacy Act 1988 — Australian Privacy Principles',
 '13 Australian Privacy Principles governing handling of personal information.',
 'AU-FEDERAL', 'PRIVACY', 'OAIC', '1988-12-17', 'medium', true, 'event_driven',
 ARRAY['fintech','health','real_estate','legal','insurance'],
 'https://www.oaic.gov.au/privacy/privacy-act'),

('SOCI-ACT-2018', 'Security of Critical Infrastructure Act 2018',
 'Obligations for owners and operators of critical infrastructure assets.',
 'AU-FEDERAL', 'CYBER', 'Home Affairs', '2018-07-11', 'high', true, 'annual',
 ARRAY['energy','telecom','health','finance','transport'],
 'https://www.homeaffairs.gov.au/soci-act'),

('CPS-230-2026', 'APRA CPS 230 — Operational Risk Management',
 'Operational risk management requirements for APRA-regulated entities.',
 'AU-FEDERAL', 'RISK_MANAGEMENT', 'APRA', '2026-07-01', 'high', true, 'annual',
 ARRAY['banking','insurance','superannuation'],
 'https://www.apra.gov.au/cps-230'),

('NCCP-ACT-2009', 'National Consumer Credit Protection Act 2009',
 'Responsible lending obligations, credit licensing, and consumer protections.',
 'AU-FEDERAL', 'CONSUMER_LAW', 'ASIC', '2009-09-01', 'high', true, 'annual',
 ARRAY['fintech','banking','insurance'],
 'https://asic.gov.au/nccp-act'),

('FAIR-TRADING-NSW', 'Fair Trading Act 1987 (NSW)',
 'Consumer protection for NSW — advertising, refunds, warranties, cooling-off periods.',
 'AU-NSW', 'CONSUMER_LAW', 'NSW Fair Trading', '1987-01-01', 'medium', false, 'continuous',
 ARRAY['retail','real_estate','services'],
 'https://www.fairtrading.nsw.gov.au'),

('AI-GUARDRAILS-2026', 'AI Mandatory Guardrails for Government',
 'Mandatory AI governance requirements for government procurement and public-facing AI systems.',
 'AU-FEDERAL', 'AI_GOVERNANCE', 'DISR', '2026-09-01', 'high', false, 'continuous',
 ARRAY['govtech','fintech','health'],
 'https://www.dta.gov.au/ai-guardrails'),

('BNPL-LICENSING-2026', 'BNPL Licensing Requirements',
 'Buy Now Pay Later providers must hold an Australian Credit Licence.',
 'AU-FEDERAL', 'CONSUMER_LAW', 'ASIC', '2026-11-01', 'high', true, 'annual',
 ARRAY['fintech'],
 'https://asic.gov.au/bnpl-licensing')
ON CONFLICT (code) DO NOTHING;

-- ── Seed Sample Organisation ──
INSERT INTO organisations (business_name, abn, entity_type, industry_sector, risk_rating, email, services_offered, states_operating, estimated_monthly_transactions, current_compliance_tools)
VALUES ('Smith Realty Group', '12345678901', 'company', 'real_estate', 'medium', 'compliance@smithrealty.com.au',
        ARRAY['property_sales','property_management','leasing'],
        ARRAY['NSW','VIC','QLD'], 150, 'spreadsheets_and_email')
ON CONFLICT (abn) DO NOTHING;

-- ── Seed Sample Deadline ──
INSERT INTO deadlines (org_id, title, description, deadline_type, due_date, priority, status)
SELECT id, 'AUSTRAC Tranche 2 Compliance', 'Complete AML/CTF compliance onboarding for all real estate agents',
       'filing', '2026-07-01', 'critical', 'pending'
FROM organisations WHERE abn = '12345678901'
AND NOT EXISTS (SELECT 1 FROM deadlines WHERE title = 'AUSTRAC Tranche 2 Compliance');

-- ── Seed Sample CDD Record ──
INSERT INTO cdd_records (org_id, customer_name, customer_type, id_type, transaction_purpose, country_of_residence, risk_level, risk_score)
SELECT id, 'Jane Smith', 'individual', 'passport', 'Property purchase — 45 Example St, Sydney NSW 2000',
       'Australia', 'low', 30
FROM organisations WHERE abn = '12345678901'
AND NOT EXISTS (SELECT 1 FROM cdd_records WHERE customer_name = 'Jane Smith');
