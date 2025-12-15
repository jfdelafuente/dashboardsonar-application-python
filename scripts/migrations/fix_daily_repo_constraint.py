#!/usr/bin/env python
"""
Migration: Fix Daily.repo Unique Constraint
============================================

Removes the incorrect unique constraint from daily.repo column.

The repo column should not be unique as multiple applications
can have the same number of repositories.

Usage:
    python scripts/migrations/fix_daily_repo_constraint.py [--config CONFIG]

Options:
    --config CONFIG    Configuration to use (Development, Production, Testing)

Created: 2024-01-15 - Fix daily.repo constraint issue
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


def fix_daily_repo_constraint(app):
    """
    Remove unique constraint from daily.repo column.

    For SQLite, we need to:
    1. Create new table without the constraint
    2. Copy data from old table
    3. Drop old table
    4. Rename new table

    Args:
        app: Flask application instance
    """
    with app.app_context():
        print("Checking database engine...")
        engine = db.engine.name

        if engine == 'sqlite':
            print("Detected SQLite database")
            print("\nApplying migration for SQLite...")

            # SQLite doesn't support ALTER TABLE DROP CONSTRAINT directly
            # We need to recreate the table

            # Step 1: Create temporary table with correct schema
            print("  1. Creating temporary table with correct schema...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS daily_new (
                    id INTEGER PRIMARY KEY,
                    aplicacion VARCHAR(64) NOT NULL UNIQUE,
                    repo INTEGER NOT NULL,
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
                print("  2. Copying data from old table...")
                # Copy data from old table to new table
                db.session.execute(db.text("""
                    INSERT INTO daily_new (
                        id, aplicacion, repo, proveedor, created_on,
                        num_bugs, num_vulnerabilities, num_code_smells,
                        num_quality, num_analisis
                    )
                    SELECT
                        id, aplicacion, repo, proveedor, created_on,
                        num_bugs, num_vulnerabilities, num_code_smells,
                        num_quality, num_analisis
                    FROM daily
                """))

                # Get count of copied records
                count_result = db.session.execute(db.text("SELECT COUNT(*) FROM daily_new")).scalar()
                print(f"     Copied {count_result} records")

                # Step 3: Drop old table
                print("  3. Dropping old table...")
                db.session.execute(db.text("DROP TABLE daily"))
            else:
                print("  2. No existing daily table found (skipped copy)")

            # Step 4: Rename new table to daily
            print("  4. Renaming new table to 'daily'...")
            db.session.execute(db.text("ALTER TABLE daily_new RENAME TO daily"))

            # Step 5: Create index on repo (non-unique)
            print("  5. Creating index on repo column...")
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS ix_daily_repo ON daily(repo)"
            ))

            db.session.commit()
            print("\n✓ Migration completed successfully for SQLite!")

        elif engine in ('postgresql', 'mysql'):
            print(f"Detected {engine.title()} database")
            print("\nApplying migration...")

            # For PostgreSQL/MySQL, we can drop the constraint directly
            try:
                # Try to drop the unique constraint
                constraint_name = 'uq_daily_repo'  # Adjust if needed
                db.session.execute(db.text(
                    f"ALTER TABLE daily DROP CONSTRAINT IF EXISTS {constraint_name}"
                ))
                db.session.commit()
                print(f"✓ Migration completed successfully for {engine.title()}!")
            except Exception as e:
                print(f"  Note: Constraint might not exist or has different name: {e}")
                print("  This is expected if constraint was never created.")

        else:
            print(f"⚠️  Unknown database engine: {engine}")
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
        result = db.session.execute(db.text(
            "PRAGMA table_info(daily)" if db.engine.name == 'sqlite'
            else "DESCRIBE daily" if db.engine.name == 'mysql'
            else "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='daily'"
        ))

        print("\nTable structure:")
        for row in result:
            print(f"  {row}")

        # Try to insert duplicate repo values (should succeed now)
        print("\nTesting duplicate repo insertion...")
        from infocodest.models.daily import Daily

        try:
            # Clean up any test data first
            db.session.query(Daily).filter(
                Daily.aplicacion.in_(['test_daily_1', 'test_daily_2'])
            ).delete()

            # Insert two applications with same repo count
            daily1 = Daily(
                aplicacion='test_daily_1',
                repo=10,  # Same repo count
                num_bugs=5,
                num_vulnerabilities=3,
                num_code_smells=20,
                num_quality=1,
                num_analisis=50
            )
            daily2 = Daily(
                aplicacion='test_daily_2',
                repo=10,  # Same repo count
                num_bugs=8,
                num_vulnerabilities=2,
                num_code_smells=15,
                num_quality=0,
                num_analisis=45
            )

            db.session.add(daily1)
            db.session.add(daily2)
            db.session.commit()

            print("  ✓ Successfully inserted duplicate repo values!")

            # Clean up test data
            db.session.delete(daily1)
            db.session.delete(daily2)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Failed to insert duplicate repo: {e}")
            return False

        print("\n✓ Migration verified successfully!")
        return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Fix daily.repo unique constraint migration'
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
        print(f"✗ Invalid configuration: {config_name}")
        return 1

    # Create Flask application
    app = create_app(config_class)

    print("\n" + "="*60)
    print("Daily.repo Constraint Fix Migration")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Database: {db.engine.url}")
    print("="*60 + "\n")

    if args.verify_only:
        success = verify_migration(app)
    else:
        # Apply migration
        success = fix_daily_repo_constraint(app)

        # Verify if successful
        if success:
            success = verify_migration(app)

    if success:
        print("\n" + "="*60)
        print("✓ Migration completed successfully!")
        print("="*60 + "\n")
        return 0
    else:
        print("\n" + "="*60)
        print("✗ Migration failed!")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
