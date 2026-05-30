# RegStack — Supabase Integration

## Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your project URL and `anon` / `service_role` API keys
3. Enable the pgcrypto extension in the Supabase dashboard

### 2. Run Migrations

**Option A: Supabase Dashboard SQL Editor**
```
Open SQL Editor → paste db/migrations/001_core_schema.sql → Run
Open SQL Editor → paste db/migrations/002_seed_data.sql → Run
```

**Option B: Supabase CLI**
```bash
supabase link --project-ref <your-project-ref>
supabase db push
```

**Option C: Direct psql**
```bash
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" \
  -f db/migrations/001_core_schema.sql

psql "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" \
  -f db/migrations/002_seed_data.sql
```

### 3. Configure Row Level Security (RLS)

Future migrations will add RLS policies. For MVP development, RLS can remain disabled.

### 4. Environment Variables

Copy `.env.example` to `.env.local` and configure:

```
# Supabase
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_KEY=<your-service-role-key>

# Storage (Cloudflare R2)
R2_ACCESS_KEY_ID=<your-r2-key>
R2_SECRET_ACCESS_KEY=<your-r2-secret>
R2_BUCKET_NAME=regstack
R2_ENDPOINT=https://<account>.r2.cloudflarestorage.com

# SMTP (PurelyMail)
SMTP_SERVER=smtp.purelymail.com
SMTP_PORT=587
SMTP_USERNAME=operator@harishabib.au
SMTP_PASSWORD=<your-password>
```

## Python Client

```python
from supabase import create_client
import os

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)

# Example: create organisation
data = supabase.table("organisations").insert({
    "business_name": "Sample Realty",
    "abn": "98765432101",
    "entity_type": "company",
    "industry_sector": "real_estate",
    "email": "admin@samplerealty.com.au",
}).execute()

# Example: assess CDD risk
result = supabase.table("cdd_records").select("*").eq("org_id", org_id).execute()

# Example: get upcoming deadlines
deadlines = supabase.table("deadlines").select("*") \
    .eq("org_id", org_id) \
    .eq("status", "pending") \
    .order("due_date", desc=False) \
    .limit(10) \
    .execute()
```

## Storage (Cloudflare R2)

Documents and evidence are stored in Cloudflare R2 buckets. Supabase's built-in storage API is not used — we use the S3-compatible R2 API directly for:
- Customer identification documents
- Compliance evidence files
- Generated reports (PDF)
- Audit trail exports

### R2 Client (Python)

```python
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
)

# Upload a compliance report
s3.upload_file(
    "report.pdf",
    os.environ["R2_BUCKET_NAME"],
    f"reports/{org_id}/{report_id}.pdf"
)
```
