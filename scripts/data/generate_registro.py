#!/usr/bin/env python
"""
Process Registry Generation Script
===================================

Creates audit/process registry records with global statistics.

The registro (registry) table contains audit logs of data processing:
- Process name and execution timestamp
- Global aggregated statistics (applications, repos, bugs, quality gates, analyses)
- Used for tracking data loads and system health monitoring

Usage:
    python scripts/generate_registro.py [--config CONFIG] [--process-name NAME]

Options:
    --config CONFIG        Configuration to use (Development, Production, Testing)
    --process-name NAME    Custom process name (default: "Registro informe Sonar")
    --date DATE            Custom date (YYYY-MM-DD, default: today)

Examples:
    # Create registry record with default name
    python scripts/generate_registro.py

    # Custom process name
    python scripts/generate_registro.py --process-name "Data Load 2025-12-15"

    # Production with custom date
    python scripts/generate_registro.py --config Production --date 2025-12-15

Created: Post-Phase 10 - Process Registry Generation
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, date
import time

# Add project root to Python path
# Script is in scripts/data/, so go up two levels to reach project root
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from infocodest import create_app
from infocodest.extensions import db
from config import config_dict

# Import models
from infocodest.models.registros import Registro
from infocodest.models.metricas import Metrica
from infocodest.models.historico import Historico

# Import repositories
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.repositories.historico_repository import HistoricoRepository


def calculate_global_statistics(app) -> Dict[str, int]:
    """Calculate global statistics from metricas and historico tables.

    Args:
        app: Flask application instance

    Returns:
        Dictionary with global statistics:
        - num_app: Number of distinct applications
        - num_repo: Number of repositories
        - num_bugs: Total bugs across all repos
        - num_quality: Number of OK quality gates
        - num_analisis: Total number of analyses
    """
    with app.app_context():
        metrica_repo = MetricaRepository()
        historico_repo = HistoricoRepository()

        print("Calculating global statistics...")

        # Count distinct applications
        num_app = metrica_repo.count_distinct_aplicaciones()
        print(f"  Applications: {num_app}")

        # Count repositories
        num_repo = metrica_repo.count_repositorios()
        print(f"  Repositories: {num_repo}")

        # Sum all bugs
        num_bugs = metrica_repo.sum_bugs()
        print(f"  Total bugs: {num_bugs}")

        # Count quality gates with OK status
        num_quality = historico_repo.count_quality_ok()
        print(f"  Quality gates OK: {num_quality}")

        # Count total analyses
        num_analisis = historico_repo.count_all()
        print(f"  Total analyses: {num_analisis}")

        stats = {
            'num_app': num_app,
            'num_repo': num_repo,
            'num_bugs': num_bugs,
            'num_quality': num_quality,
            'num_analisis': num_analisis
        }

        print("✓ Global statistics calculated")
        return stats


def create_registry_record(app, process_name: str, registry_date: date, stats: Dict[str, int]) -> bool:
    """Create a registry record with process information and statistics.

    Args:
        app: Flask application instance
        process_name: Name of the process being registered
        registry_date: Date of the registry record
        stats: Dictionary with statistics

    Returns:
        True if successful, False otherwise
    """
    with app.app_context():
        try:
            print(f"Creating registry record for '{process_name}'...")

            registro = Registro(
                proceso=process_name,
                created_on=registry_date,
                num_app=stats['num_app'],
                num_repo=stats['num_repo'],
                num_bugs=stats['num_bugs'],
                num_quality=stats['num_quality'],
                num_analisis=stats['num_analisis']
            )

            db.session.add(registro)
            db.session.commit()

            print(f"✓ Registry record created (ID: {registro.id})")
            return True

        except Exception as e:
            print(f"✗ Error creating registry record: {e}")
            db.session.rollback()
            return False


def display_registry_summary(process_name: str, registry_date: date, stats: Dict[str, int]):
    """Display summary of the registry record.

    Args:
        process_name: Process name
        registry_date: Registry date
        stats: Statistics dictionary
    """
    print("\n" + "="*60)
    print("Registry Record Summary")
    print("="*60)
    print(f"Process: {process_name}")
    print(f"Date: {registry_date}")
    print("-" * 60)
    print(f"Applications:    {stats['num_app']:>6}")
    print(f"Repositories:    {stats['num_repo']:>6}")
    print(f"Total Bugs:      {stats['num_bugs']:>6}")
    print(f"Quality OK:      {stats['num_quality']:>6}")
    print(f"Total Analyses:  {stats['num_analisis']:>6}")
    print("="*60)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Generate process registry record with global statistics'
    )
    parser.add_argument(
        '--config',
        type=str,
        choices=['Development', 'Production', 'Testing'],
        default='Development',
        help='Configuration environment (default: Development)'
    )
    parser.add_argument(
        '--process-name',
        type=str,
        default='Registro informe Sonar',
        help='Process name for the registry (default: "Registro informe Sonar")'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Registry date (YYYY-MM-DD, default: today)'
    )

    args = parser.parse_args()

    # Parse date
    if args.date:
        try:
            registry_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"✗ Invalid date format: {args.date}. Use YYYY-MM-DD")
            return 1
    else:
        registry_date = date.today()

    # Get configuration
    config_name = args.config
    config_class = config_dict.get(config_name)

    if not config_class:
        print(f"✗ Invalid configuration: {config_name}")
        return 1

    # Create Flask application
    app = create_app(config_class)

    print("\n" + "="*60)
    print("Process Registry Generation Script")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Process: {args.process_name}")
    print(f"Date: {registry_date}")
    print("="*60 + "\n")

    start_time = time.time()

    try:
        # Calculate global statistics
        stats = calculate_global_statistics(app)
        print()

        # Create registry record
        success = create_registry_record(app, args.process_name, registry_date, stats)

        if not success:
            print("\n✗ Failed to create registry record")
            return 1

        # Display summary
        duration = time.time() - start_time
        display_registry_summary(args.process_name, registry_date, stats)
        print(f"\nDuration: {duration:.2f} seconds")
        print("\n✓ Registry record created successfully!\n")

    except Exception as e:
        print(f"\n✗ Error during registry generation: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
