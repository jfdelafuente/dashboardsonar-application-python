"""
Migrations Package
==================

Database schema migrations for the Dashboard Sonar application.

This package contains manual migration scripts for schema changes
that cannot be handled by Flask-Migrate or require special handling.

Migrations:
    - fix_stats_repos_constraint.py: Remove unique constraint from stats.repos
    - fix_daily_repo_constraint.py: Remove unique constraint from daily.repo
    - fix_daily_aplicacion_constraint.py: Remove unique constraint from daily.aplicacion

Usage:
    python scripts/migrations/MIGRATION_NAME.py [--config CONFIG]

Examples:
    # Fix stats table (repos column)
    python scripts/migrations/fix_stats_repos_constraint.py

    # Fix daily table (repo column)
    python scripts/migrations/fix_daily_repo_constraint.py

    # Fix daily table (aplicacion column) - IMPORTANT for daily snapshots
    python scripts/migrations/fix_daily_aplicacion_constraint.py

    # Verify only (no changes)
    python scripts/migrations/fix_daily_aplicacion_constraint.py --verify-only

    # Run all daily table migrations in order
    python scripts/migrations/fix_daily_repo_constraint.py && \
    python scripts/migrations/fix_daily_aplicacion_constraint.py

Created: 2024-01-15 - Migrations support
"""

__version__ = "1.0.0"
