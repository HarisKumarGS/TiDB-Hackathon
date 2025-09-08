# Alembic Database Migrations

This directory contains Alembic migration scripts for the Crash Lens application database.

## Setup

1. **Install dependencies** (if not already done):
   ```bash
   cd /Users/hariskumargs/Documents/Personal/TiDB-Hackathon/crash-lens-app/backend
   pip install -e .
   ```

2. **Configure database connection**:
   The database URL is configured in `alembic.ini`. Make sure the database exists before running migrations.

## Migration Commands

### Create a new migration
```bash
cd /Users/hariskumargs/Documents/Personal/TiDB-Hackathon/crash-lens-app/backend
python -m alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
python -m alembic upgrade head
```

### Rollback migrations
```bash
# Rollback one migration
python -m alembic downgrade -1

# Rollback to specific revision
python -m alembic downgrade <revision_id>

# Rollback all migrations
python -m alembic downgrade base
```

### Check migration status
```bash
python -m alembic current
python -m alembic history
```

## Database Schema

### Tables Created

1. **repository**
   - `id` (String, Primary Key)
   - `name` (String, 255 chars)
   - `url` (String, 500 chars)
   - `description` (Text)
   - `created_at` (DateTime with timezone)
   - `updated_at` (DateTime with timezone)

2. **crash**
   - `id` (String, Primary Key)
   - `component` (String, 255 chars)
   - `error_type` (String, 255 chars)
   - `severity` (String, 50 chars)
   - `status` (String, 50 chars)
   - `impacted_users` (Integer)
   - `comment` (String, 500 chars, nullable)
   - `repository_id` (String, Foreign Key to repository.id)
   - `error_log` (String, 500 chars, nullable)
   - `created_at` (DateTime with timezone)
   - `updated_at` (DateTime with timezone)

3. **crash_rca**
   - `id` (String, Primary Key)
   - `crash_id` (String, Foreign Key to crash.id)
   - `description` (Text, nullable)
   - `problem_identification` (Text, nullable)
   - `data_collection` (Text, nullable)
   - `analysis` (Text, nullable)
   - `root_cause_identification` (Text, nullable)
   - `solution` (Text, nullable)
   - `author` (Array of Strings, nullable)
   - `supporting_documents` (Array of Strings, nullable)
   - `created_at` (DateTime with timezone)
   - `updated_at` (DateTime with timezone)

### Indexes Created

- `ix_crash_repository_id` on `crash.repository_id`
- `ix_crash_severity` on `crash.severity`
- `ix_crash_status` on `crash.status`
- `ix_crash_created_at` on `crash.created_at`
- `ix_crash_rca_crash_id` on `crash_rca.crash_id`

## SQLAlchemy Models

The corresponding SQLAlchemy models are defined in `src/app/models/sqlalchemy_models.py`:

- `Repository`
- `Crash`
- `CrashRCA`

These models include relationships and can be used for ORM operations in the application.

## Notes

- All timestamps use timezone-aware DateTime fields
- Foreign key constraints ensure referential integrity
- Array fields are used for `author` and `supporting_documents` in the RCA table
- Indexes are created for commonly queried fields to improve performance
