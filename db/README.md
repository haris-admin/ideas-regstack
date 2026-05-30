# Database Migration

A standalone, zero-dependency SQLite database migration for local development.

## Workflow

```
Local Dev (SQLite) → Staging (Supabase PG) → Production (Supabase PG)
```

## Usage

### Local Development (SQLite)

```bash
python db/migrate.py
```

### Supabase Staging/Production

```bash
python db/migrate.py --to-pg --url "postgresql://user:password@db.xxx.supabase.co:5432/postgres"
```

### Verify Schema

```bash
python db/migrate.py --verify
```
