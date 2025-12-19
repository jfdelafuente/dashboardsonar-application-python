#!/usr/bin/env python
"""
Migration: Fix Daily.repo Data Type
====================================

Changes the daily.repo column from INTEGER to VARCHAR(128).

The repo column should store repository names (strings) like 'abacus-application-java',
not repository counts (integers).

This migration:
- Changes repo from INTEGER to VARCHAR(128)
- Preserves existing data (if any integer values exist, they will be converted to strings)
- Maintains the index on repo column

Usage:
    python scripts/migrations/fix_daily_repo_datatype.py [--config CONFIG]

Options:
    --config CONFIG    Configuration to use (Development, Production, Testing)

Created: 2025-12-19 - Fix daily.repo data type issue
"""

import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from infocodest import create_app
from infocodest.extensions import db
from config import config_dict


def fix_daily_repo_datatype(app):
    """
    Change daily.repo column from INTEGER to VARCHAR(128).

    For SQLite, we need to:
    1. Create new table with correct data type
    2. Copy data from old table
    3. Drop old table
    4. Rename new table

    For PostgreSQL, we can use ALTER COLUMN.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        print("Checking database engine...")
        engine = db.engine.name

        if engine == 'sqlite':
            print("Detected SQLite database")
            print("\nApplying migration for SQLite...")

            # SQLite doesn't support ALTER TABLE ALTER COLUMN directly
            # We need to recreate the table

            # Step 1: Create temporary table with correct schema
            print("  1. Creating temporary table with correct schema...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS daily_new (
                    id INTEGER PRIMARY KEY,
                    aplicacion VARCHAR(64) NOT NULL,
                    repo VARCHAR(128) NOT NULL,
                    proveedor TEXT,
                    created_on DATETIME,
                    num_bugs INTEGER NOT NULL,
                    num_vulnerabilities INTEGER NOT NULL,
                    num_code_smells INTEGER NOT NULL,
                    num_quality INTEGER NOT NULL,
                    num_analisis INTEGER NOT NULL
                )
            """))

            # Step 2: Check if daily table exists and has data
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='daily'"
            )).fetchone()

            if result:
                print("  2. Checking for existing data...")
                count_result = db.session.execute(db.text("SELECT COUNT(*) FROM daily")).scalar()
                print(f"     Found {count_result} existing records")

                if count_result > 0:
                    print("  3. Copying data from old table (converting repo to string)...")
                    # Copy data from old table to new table, converting repo to string
                    db.session.execute(db.text("""
                        INSERT INTO daily_new (
                            id, aplicacion, repo, proveedor, created_on,
                            num_bugs, num_vulnerabilities, num_code_smells,
                            num_quality, num_analisis
                        )
                        SELECT
                            id, aplicacion, CAST(repo AS TEXT), proveedor, created_on,
                            num_bugs, num_vulnerabilities, num_code_smells,
                            num_quality, num_analisis
                        FROM daily
                    """))

                    # Verify copied records
                    new_count = db.session.execute(db.text("SELECT COUNT(*) FROM daily_new")).scalar()
                    print(f"     Copied {new_count} records")

                # Step 4: Drop old table
                print("  4. Dropping old table...")
                db.session.execute(db.text("DROP TABLE daily"))
            else:
                print("  2. No existing daily table found (creating fresh)")

            # Step 5: Rename new table to daily
            print("  5. Renaming new table to 'daily'...")
            db.session.execute(db.text("ALTER TABLE daily_new RENAME TO daily"))

            # Step 6: Create indexes
            print("  6. Creating indexes...")
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS ix_daily_aplicacion ON daily(aplicacion)"
            ))
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS ix_daily_repo ON daily(repo)"
            ))
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS idx_daily_aplicacion_date ON daily(aplicacion, created_on)"
            ))

            db.session.commit()
            print("\n[OK] Migration completed successfully for SQLite!")

        elif engine == 'postgresql':
            print("Detected PostgreSQL database")
            print("\nApplying migration for PostgreSQL...")

            try:
                # Step 1: Check if column is already VARCHAR
                result = db.session.execute(db.text("""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_name='daily' AND column_name='repo'
                """)).fetchone()

                if result:
                    current_type = result[0]
                    print(f"  Current repo column type: {current_type}")

                    if 'varchar' in current_type.lower() or 'character' in current_type.lower():
                        print("  Column is already VARCHAR - no migration needed!")
                        return True

                # Step 2: Alter column type
                print("  Altering column type from INTEGER to VARCHAR(128)...")
                db.session.execute(db.text("""
                    ALTER TABLE daily
                    ALTER COLUMN repo TYPE VARCHAR(128) USING repo::VARCHAR(128)
                """))

                db.session.commit()
                print("\n[OK] Migration completed successfully for PostgreSQL!")

            except Exception as e:
                db.session.rollback()
                print(f"\n[ERROR] Error during PostgreSQL migration: {e}")
                import traceback
                traceback.print_exc()
                return False

        elif engine == 'mysql':
            print("Detected MySQL database")
            print("\nApplying migration for MySQL...")

            try:
                # Step 1: Check current column type
                result = db.session.execute(db.text("""
                    SELECT DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'daily'
                    AND COLUMN_NAME = 'repo'
                """)).fetchone()

                if result:
                    current_type = result[0]
                    print(f"  Current repo column type: {current_type}")

                    if 'varchar' in current_type.lower() or 'char' in current_type.lower():
                        print("  Column is already VARCHAR - no migration needed!")
                        return True

                # Step 2: Alter column type
                print("  Altering column type from INTEGER to VARCHAR(128)...")
                db.session.execute(db.text("""
                    ALTER TABLE daily
                    MODIFY COLUMN repo VARCHAR(128) NOT NULL
                """))

                db.session.commit()
                print("\n[OK] Migration completed successfully for MySQL!")

            except Exception as e:
                db.session.rollback()
                print(f"\n[ERROR] Error during MySQL migration: {e}")
                import traceback
                traceback.print_exc()
                return False

        else:
            print(f"[WARNING] Unknown database engine: {engine}")
            print("  Please apply migration manually.")
            return False

        return True


def verify_migration(app):
    """
    Verify that the migration was successful.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        print("\nVerifying migration...")

        # Check table structure
        engine = db.engine.name

        if engine == 'sqlite':
            result = db.session.execute(db.text("PRAGMA table_info(daily)"))
            print("\nTable structure:")
            for row in result:
                print(f"  {row}")
        elif engine == 'postgresql':
            result = db.session.execute(db.text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name='daily'
                ORDER BY ordinal_position
            """))
            print("\nTable structure:")
            for row in result:
                print(f"  {row}")
        elif engine == 'mysql':
            result = db.session.execute(db.text("DESCRIBE daily"))
            print("\nTable structure:")
            for row in result:
                print(f"  {row}")

        # Try to insert string repo value (should succeed now)
        print("\nTesting string repo insertion...")
        from infocodest.models.daily import Daily
        from datetime import date

        try:
            # Clean up any test data first
            db.session.query(Daily).filter(
                Daily.aplicacion == 'test_migration_app'
            ).delete()
            db.session.commit()

            # Insert application with string repo name
            daily_test = Daily(
                aplicacion='test_migration_app',
                repo='test-repository-name',  # String repo name
                proveedor='test-provider',
                created_on=date.today(),
                num_bugs=5,
                num_vulnerabilities=3,
                num_code_smells=20,
                num_quality=1,
                num_analisis=50
            )

            db.session.add(daily_test)
            db.session.commit()

            print("  [OK] Successfully inserted string repo value: 'test-repository-name'")

            # Verify the data
            retrieved = db.session.query(Daily).filter(
                Daily.aplicacion == 'test_migration_app'
            ).first()

            if retrieved and retrieved.repo == 'test-repository-name':
                print(f"  [OK] Successfully retrieved repo: '{retrieved.repo}'")
            else:
                print(f"  [ERROR] Data verification failed")
                return False

            # Clean up test data
            db.session.delete(daily_test)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"  [ERROR] Failed to insert string repo: {e}")
            import traceback
            traceback.print_exc()
            return False

        print("\n[OK] Migration verified successfully!")
        return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Fix daily.repo data type migration'
    )
    parser.add_argument(
        '--config',
        type=str,
        choices=['Development', 'Production', 'Testing'],
        default='Development',
        help='Configuration environment (default: Development)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify migration without applying'
    )

    args = parser.parse_args()

    # Get configuration
    config_name = args.config
    config_class = config_dict.get(config_name)

    if not config_class:
        print(f"[ERROR] Invalid configuration: {config_name}")
        return 1

    # Create Flask application
    app = create_app(config_class)

    with app.app_context():
        print("\n" + "="*60)
        print("Daily.repo Data Type Fix Migration")
        print("="*60)
        print(f"Configuration: {config_name}")
        print(f"Database: {db.engine.url}")
        print(f"Action: INTEGER -> VARCHAR(128)")
        print("="*60 + "\n")

        if args.verify_only:
            success = verify_migration(app)
        else:
            # Apply migration
            success = fix_daily_repo_datatype(app)

            # Verify if successful
            if success:
                success = verify_migration(app)

        if success:
            print("\n" + "="*60)
            print("[OK] Migration completed successfully!")
            print("  - daily.repo is now VARCHAR(128)")
            print("  - Can store repository names like 'abacus-application-java'")
            print("="*60 + "\n")
            return 0
        else:
            print("\n" + "="*60)
            print("[ERROR] Migration failed!")
            print("="*60 + "\n")
            return 1


if __name__ == "__main__":
    sys.exit(main())
