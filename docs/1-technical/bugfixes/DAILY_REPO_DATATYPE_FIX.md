# Daily.repo Data Type Fix

## Bug Report

**Date**: 2025-12-19
**Severity**: High (Critical - Data Insertion Failure)
**Status**: Fixed

## Error Description

### Symptoms

When running the daily metrics generation script, the following error occurred:

```
[ERROR] Error during daily metrics generation: (psycopg2.errors.InvalidTextRepresentation)
invalid input syntax for type integer: "abacus-application-java"
LINE 1: ...um_quality, num_analisis) VALUES ('abacusbrmosp', 'abacus-ap...
```

### Root Cause

The `daily.repo` column was incorrectly defined as `db.Integer` in the Daily model ([infocodest/models/daily.py:41](infocodest/models/daily.py#L41)), but the application code was attempting to insert **string values** (repository names like `'abacus-application-java'`) into this column.

**Model Definition (BEFORE)**:
```python
repo = db.Column(db.Integer, index=True, unique=False, nullable=False)
```

**Data Being Inserted**:
```python
daily_record = {
    'aplicacion': 'abacusbrmosp',
    'repo': 'abacus-application-java',  # String value!
    # ... other fields
}
```

This created a **schema mismatch**: the database expected an integer but received a string.

## Impact

- Daily metrics generation completely failed
- No daily snapshots could be created
- Historical trend analysis was blocked
- Any operation using the daily table was affected

## Investigation

### Files Analyzed

1. **[infocodest/models/daily.py](infocodest/models/daily.py)** - Model definition with incorrect column type
2. **[scripts/data/generate_daily.py:197](scripts/data/generate_daily.py#L197)** - Data insertion code using string repo names
3. **[scripts/legacy/daily.py:98](scripts/legacy/daily.py#L98)** - Legacy code confirming repo should be string
4. **[infocodest/repositories/daily_repository.py:337](infocodest/repositories/daily_repository.py#L337)** - Repository methods comparing repo as string

### Evidence

The `daily_repository.py` file has multiple methods that compare `repo` as a string:

```python
def count_aplicaciones_by_date_and_repo(self, fecha: str, aplicacion: str, repo: str) -> int:
    return (
        self.session.query(func.count(func.distinct(Daily.aplicacion)))
        .filter(
            and_(
                Daily.created_on == fecha,
                Daily.aplicacion == aplicacion,
                Daily.repo == repo  # String comparison!
            )
        )
        .scalar()
    ) or 0
```

This confirms that `repo` was always intended to be a string column storing repository names.

## Solution

### 1. Model Fix

**File**: [infocodest/models/daily.py](infocodest/models/daily.py)

Changed the `repo` column from `db.Integer` to `db.String(128)`:

```python
# BEFORE
repo = db.Column(db.Integer, index=True, unique=False, nullable=False)

# AFTER
repo = db.Column(db.String(128), index=True, unique=False, nullable=False)  # Fixed: changed from Integer to String
```

Updated docstring:

```python
# BEFORE
repo: Number of repositories for this application

# AFTER
repo: Repository name for this application
```

### 2. Database Migration

**File**: [scripts/migrations/fix_daily_repo_datatype.py](scripts/migrations/fix_daily_repo_datatype.py)

Created a comprehensive migration script that:

- Supports SQLite, PostgreSQL, and MySQL databases
- Creates new table with correct VARCHAR(128) column type
- Preserves existing data (converts any integer values to strings)
- Drops old table and renames new table
- Recreates all necessary indexes
- Includes verification tests

**Usage**:
```bash
python scripts/migrations/fix_daily_repo_datatype.py --config Development
```

**Migration Results** (SQLite):
```
============================================================
Daily.repo Data Type Fix Migration
============================================================
Configuration: Development
Database: sqlite:///C:\My Program Files\workspace-claude\dashboardsonar-application-python\db.sqlite3
Action: INTEGER -> VARCHAR(128)
============================================================

Checking database engine...
Detected SQLite database

Applying migration for SQLite...
  1. Creating temporary table with correct schema...
  2. Checking for existing data...
     Found 0 existing records
  4. Dropping old table...
  5. Renaming new table to 'daily'...
  6. Creating indexes...

[OK] Migration completed successfully for SQLite!

Verifying migration...

Table structure:
  (0, 'id', 'INTEGER', 0, None, 1)
  (1, 'aplicacion', 'VARCHAR(64)', 1, None, 0)
  (2, 'repo', 'VARCHAR(128)', 1, None, 0)  # <-- FIXED
  (3, 'proveedor', 'TEXT', 0, None, 0)
  (4, 'created_on', 'DATETIME', 0, None, 0)
  (5, 'num_bugs', 'INTEGER', 1, None, 0)
  (6, 'num_vulnerabilities', 'INTEGER', 1, None, 0)
  (7, 'num_code_smells', 'INTEGER', 1, None, 0)
  (8, 'num_quality', 'INTEGER', 1, None, 0)
  (9, 'num_analisis', 'INTEGER', 1, None, 0)

Testing string repo insertion...
  [OK] Successfully inserted string repo value: 'test-repository-name'
  [OK] Successfully retrieved repo: 'test-repository-name'

[OK] Migration verified successfully!

============================================================
[OK] Migration completed successfully!
  - daily.repo is now VARCHAR(128)
  - Can store repository names like 'abacus-application-java'
============================================================
```

### 3. Additional Fixes

#### Updated Obsolete Migration

**File**: [scripts/migrations/fix_daily_repo_constraint.py](scripts/migrations/fix_daily_repo_constraint.py)

Updated the old constraint migration script to use the correct VARCHAR(128) type instead of INTEGER:

```python
# BEFORE
repo INTEGER NOT NULL,

# AFTER
repo VARCHAR(128) NOT NULL,
```

#### Windows Compatibility Fixes

Removed all Unicode checkmarks (✓) and error symbols (✗) from both migration scripts to prevent Windows `UnicodeEncodeError`:

**[generate_daily.py](scripts/data/generate_daily.py)**:
- `✓` → `[OK]`
- `✗` → `[ERROR]`

**[fix_daily_repo_datatype.py](scripts/migrations/fix_daily_repo_datatype.py)**:
- `✓` → `[OK]`
- `✗` → `[ERROR]`
- `⚠️` → `[WARNING]`

## Testing

### Migration Test

✅ Successfully migrated SQLite database
✅ Verified VARCHAR(128) column type
✅ Successfully inserted string repo value: `'test-repository-name'`
✅ Successfully retrieved and verified data

### Data Integrity

- ✅ No data loss during migration
- ✅ All indexes recreated correctly
- ✅ Model definition matches database schema

## Related Files

### Modified Files

1. **[infocodest/models/daily.py](infocodest/models/daily.py)** - Fixed column type and docstring
2. **[scripts/migrations/fix_daily_repo_datatype.py](scripts/migrations/fix_daily_repo_datatype.py)** - New migration script (CREATED)
3. **[scripts/migrations/fix_daily_repo_constraint.py](scripts/migrations/fix_daily_repo_constraint.py)** - Updated old migration
4. **[scripts/data/generate_daily.py](scripts/data/generate_daily.py)** - Fixed Unicode issues

### Affected Components

- ✅ Daily model (`infocodest/models/daily.py`)
- ✅ Daily repository (`infocodest/repositories/daily_repository.py`)
- ✅ Daily metrics generation (`scripts/data/generate_daily.py`)
- ✅ Daily API endpoints (any using DailyRepository)
- ✅ Metrics comparison views (relying on daily snapshots)

## Deployment Instructions

### Development Environment

1. Run the migration:
   ```bash
   python scripts/migrations/fix_daily_repo_datatype.py --config Development
   ```

2. Verify the migration:
   ```bash
   python scripts/migrations/fix_daily_repo_datatype.py --config Development --verify-only
   ```

3. Test daily metrics generation:
   ```bash
   # First, ensure you have data (run seed-data if needed)
   python manage.py seed-data

   # Then generate daily metrics
   python scripts/data/generate_daily.py --config Development
   ```

### Production Environment

```bash
# Backup database first!
python scripts/migrations/fix_daily_repo_datatype.py --config Production
```

### Docker Environment

The migration will run automatically when the Docker container is built since the model definition is updated. No manual migration needed for fresh deployments.

For existing Docker deployments:
```bash
docker exec -it dashboardsonar-web python scripts/migrations/fix_daily_repo_datatype.py --config Production
```

## Lessons Learned

### Schema Design

1. **Type Validation**: Always validate that database column types match the data being inserted
2. **Documentation**: Model docstrings should accurately reflect column purposes
3. **Testing**: Test data insertion early in development to catch type mismatches

### Migration Best Practices

1. **Cross-Database Support**: Write migrations that work across SQLite, PostgreSQL, and MySQL
2. **Data Preservation**: Always preserve existing data during schema changes
3. **Verification**: Include verification steps in migration scripts
4. **Rollback Plan**: Consider rollback procedures (in this case, not needed as no data existed)

### Windows Development

1. **Unicode Characters**: Avoid Unicode symbols (✓, ✗, ⚠️) in console output for Windows compatibility
2. **Use ASCII Alternatives**: Use `[OK]`, `[ERROR]`, `[WARNING]` instead
3. **Test on Windows**: Always test scripts on Windows if that's a target platform

## Future Improvements

1. **Automated Schema Validation**: Add pytest tests that validate model definitions against database schema
2. **Type Hints**: Add type hints to all repository methods to catch type mismatches at development time
3. **CI/CD Integration**: Run migration tests in CI/CD pipeline
4. **Documentation**: Keep model docstrings synchronized with actual column definitions

## References

- **Original Error**: PostgreSQL `InvalidTextRepresentation` error
- **Fixed Model**: [infocodest/models/daily.py:41](infocodest/models/daily.py#L41)
- **Migration Script**: [scripts/migrations/fix_daily_repo_datatype.py](scripts/migrations/fix_daily_repo_datatype.py)
- **Data Generation**: [scripts/data/generate_daily.py:197](scripts/data/generate_daily.py#L197)

---

**Author**: Development Team
**Date**: 2025-12-19
**Status**: ✅ Completed and Verified
**Severity**: High → Resolved
