#!/usr/bin/env python
"""
Migration: Fix Stats.repos Unique Constraint
=============================================

Removes the incorrect unique constraint from stats.repos column.

The repos column should not be unique as multiple applications
can have the same number of repositories.

Usage:
    python scripts/migrations/fix_stats_repos_constraint.py [--config CONFIG]

Options:
    --config CONFIG    Configuration to use (Development, Production, Testing)

Created: 2024-01-15 - Fix stats.repos constraint issue
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


def fix_stats_repos_constraint(app):
    """
    Remove unique constraint from stats.repos column.

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
                CREATE TABLE IF NOT EXISTS stats_new (
                    id INTEGER PRIMARY KEY,
                    aplicacion VARCHAR(64) NOT NULL UNIQUE,
                    repos INTEGER NOT NULL,
                    reliability_label TEXT,
                    reliability_rating INTEGER NOT NULL,
                    sqale_label TEXT,
                    sqale_rating INTEGER NOT NULL,
                    security_label TEXT,
                    security_rating INTEGER NOT NULL,
                    alert_status_label TEXT,
                    alert_status_ok INTEGER NOT NULL,
                    dloc_label TEXT,
                    dloc_rating INTEGER NOT NULL,
                    coverage_label TEXT,
                    coverage_rating INTEGER NOT NULL
                )
            """))

            # Step 2: Check if stats table exists and has data
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='stats'"
            )).fetchone()

            if result:
                print("  2. Copying data from old table...")
                # Copy data from old table to new table
                db.session.execute(db.text("""
                    INSERT INTO stats_new (
                        id, aplicacion, repos,
                        reliability_label, reliability_rating,
                        sqale_label, sqale_rating,
                        security_label, security_rating,
                        alert_status_label, alert_status_ok,
                        dloc_label, dloc_rating,
                        coverage_label, coverage_rating
                    )
                    SELECT
                        id, aplicacion, repos,
                        reliability_label, reliability_rating,
                        sqale_label, sqale_rating,
                        security_label, security_rating,
                        alert_status_label, alert_status_ok,
                        dloc_label, dloc_rating,
                        coverage_label, coverage_rating
                    FROM stats
                """))

                # Get count of copied records
                count_result = db.session.execute(db.text("SELECT COUNT(*) FROM stats_new")).scalar()
                print(f"     Copied {count_result} records")

                # Step 3: Drop old table
                print("  3. Dropping old table...")
                db.session.execute(db.text("DROP TABLE stats"))
            else:
                print("  2. No existing stats table found (skipped copy)")

            # Step 4: Rename new table to stats
            print("  4. Renaming new table to 'stats'...")
            db.session.execute(db.text("ALTER TABLE stats_new RENAME TO stats"))

            # Step 5: Create index on repos (non-unique)
            print("  5. Creating index on repos column...")
            db.session.execute(db.text(
                "CREATE INDEX IF NOT EXISTS ix_stats_repos ON stats(repos)"
            ))

            db.session.commit()
            print("\n✓ Migration completed successfully for SQLite!")

        elif engine in ('postgresql', 'mysql'):
            print(f"Detected {engine.title()} database")
            print("\nApplying migration...")

            # For PostgreSQL/MySQL, we can drop the constraint directly
            try:
                # Try to drop the unique constraint
                constraint_name = 'uq_stats_repos'  # Adjust if needed
                db.session.execute(db.text(
                    f"ALTER TABLE stats DROP CONSTRAINT IF EXISTS {constraint_name}"
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
            "PRAGMA table_info(stats)" if db.engine.name == 'sqlite'
            else "DESCRIBE stats" if db.engine.name == 'mysql'
            else "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='stats'"
        ))

        print("\nTable structure:")
        for row in result:
            print(f"  {row}")

        # Try to insert duplicate repos values (should succeed now)
        print("\nTesting duplicate repos insertion...")
        from infocodest.models.stat import Stat

        try:
            # Clean up any test data first
            db.session.query(Stat).filter(
                Stat.aplicacion.in_(['test_app_1', 'test_app_2'])
            ).delete()

            # Insert two applications with same repos count
            stat1 = Stat(
                aplicacion='test_app_1',
                repos=5,  # Same repos count
                reliability_rating=1,
                sqale_rating=1,
                security_rating=1,
                alert_status_ok=1,
                dloc_rating=1,
                coverage_rating=1
            )
            stat2 = Stat(
                aplicacion='test_app_2',
                repos=5,  # Same repos count
                reliability_rating=2,
                sqale_rating=2,
                security_rating=2,
                alert_status_ok=2,
                dloc_rating=2,
                coverage_rating=2
            )

            db.session.add(stat1)
            db.session.add(stat2)
            db.session.commit()

            print("  ✓ Successfully inserted duplicate repos values!")

            # Clean up test data
            db.session.delete(stat1)
            db.session.delete(stat2)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Failed to insert duplicate repos: {e}")
            return False

        print("\n✓ Migration verified successfully!")
        return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Fix stats.repos unique constraint migration'
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
    print("Stats.repos Constraint Fix Migration")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Database: {db.engine.url}")
    print("="*60 + "\n")

    if args.verify_only:
        success = verify_migration(app)
    else:
        # Apply migration
        success = fix_stats_repos_constraint(app)

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
