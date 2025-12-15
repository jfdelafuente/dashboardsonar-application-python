"""
Migrations Package
==================

Database schema migrations for the Dashboard Sonar application.

This package contains manual migration scripts for schema changes
that cannot be handled by Flask-Migrate or require special handling.

Migrations:
    - fix_stats_repos_constraint.py: Remove unique constraint from stats.repos

Usage:
    python scripts/migrations/MIGRATION_NAME.py [--config CONFIG]

Created: 2024-01-15 - Migrations support
"""

__version__ = "1.0.0"
