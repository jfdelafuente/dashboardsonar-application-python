#!/usr/bin/env python
"""
Daily Metrics Generation Script
================================

Generates daily snapshots of aggregated metrics per repository.

The daily table contains time-series data with daily aggregations:
- Metrics aggregated per application + repository + date
- Includes: bugs, vulnerabilities, code_smells, quality gates, analysis count
- Used for historical trend analysis and comparisons

Usage:
    python scripts/generate_daily.py [--config CONFIG] [--date DATE]

Options:
    --config CONFIG    Configuration to use (Development, Production, Testing)
    --date DATE        Specific date for snapshot (YYYY-MM-DD, default: today)
    --clear-date       Clear existing records for the specified date before generating
    --batch-size N     Batch size for bulk inserts (default: 100)

Examples:
    # Generate daily snapshot for today
    python scripts/generate_daily.py

    # Generate for specific date
    python scripts/generate_daily.py --date 2025-12-15

    # Regenerate today's snapshot (clear + generate)
    python scripts/generate_daily.py --clear-date

    # Production environment
    python scripts/generate_daily.py --config Production

Created: Post-Phase 10 - Daily Metrics Generation
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
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
from infocodest.models.daily import Daily
from infocodest.models.metricas import Metrica
from infocodest.models.historico import Historico
from infocodest.models.proveedor import Proveedor

# Import repositories
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.repositories.historico_repository import HistoricoRepository
from infocodest.repositories.proveedor_repository import ProveedorRepository


def get_distinct_aplicaciones(metrica_repo) -> List[str]:
    """Get list of distinct applications.

    Args:
        metrica_repo: MetricaRepository instance

    Returns:
        List of application names
    """
    return metrica_repo.get_distinct_aplicaciones()


def get_repos_by_aplicacion(metrica_repo, aplicacion: str) -> List[str]:
    """Get list of repositories for an application.

    Args:
        metrica_repo: MetricaRepository instance
        aplicacion: Application name

    Returns:
        List of repository names
    """
    metricas = metrica_repo.get_by_aplicacion(aplicacion)
    repos = list(set([m.repo for m in metricas]))
    return repos


def get_proveedor_for_aplicacion(proveedor_repo, aplicacion: str) -> str:
    """Get provider name for an application.

    Args:
        proveedor_repo: ProveedorRepository instance
        aplicacion: Application name

    Returns:
        Provider name or empty string
    """
    proveedor = proveedor_repo.get_by_aplicacion(aplicacion)
    if proveedor:
        return proveedor.proveedor
    return ""


def calculate_repo_metrics(metrica_repo, historico_repo, aplicacion: str, repo: str) -> Dict[str, int]:
    """Calculate aggregated metrics for a specific repository.

    Args:
        metrica_repo: MetricaRepository instance
        historico_repo: HistoricoRepository instance
        aplicacion: Application name
        repo: Repository name

    Returns:
        Dictionary with aggregated metrics
    """
    # Aggregate from Metricas table
    metricas = (
        metrica_repo.session.query(Metrica)
        .filter(
            Metrica.aplicacion == aplicacion,
            Metrica.repo == repo
        )
        .all()
    )

    num_bugs = sum(m.bugs or 0 for m in metricas)
    num_vulnerabilities = sum(m.vulnerabilities or 0 for m in metricas)
    num_code_smells = sum(m.code_smells or 0 for m in metricas)

    # Count quality gates and analysis from Historico
    num_analisis = (
        historico_repo.session.query(Historico)
        .filter(
            Historico.aplicacion == aplicacion,
            Historico.repo == repo
        )
        .count()
    )

    num_quality = (
        historico_repo.session.query(Historico)
        .filter(
            Historico.aplicacion == aplicacion,
            Historico.repo == repo,
            Historico.alert_status == 'OK'
        )
        .count()
    )

    return {
        'num_bugs': num_bugs,
        'num_vulnerabilities': num_vulnerabilities,
        'num_code_smells': num_code_smells,
        'num_quality': num_quality,
        'num_analisis': num_analisis
    }


def extract_daily_metrics(app, snapshot_date: date) -> List[Dict[str, Any]]:
    """Extract daily metrics for all repositories.

    Args:
        app: Flask application instance
        snapshot_date: Date for the snapshot

    Returns:
        List of daily metric records
    """
    with app.app_context():
        metrica_repo = MetricaRepository()
        historico_repo = HistoricoRepository()
        proveedor_repo = ProveedorRepository()

        print(f"Extracting daily metrics for {snapshot_date}...")
        aplicaciones = get_distinct_aplicaciones(metrica_repo)
        print(f"Found {len(aplicaciones)} applications")

        daily_records = []
        total_repos = 0

        for i, app_name in enumerate(aplicaciones, 1):
            print(f"  Processing application {i}/{len(aplicaciones)}: {app_name}")

            repos = get_repos_by_aplicacion(metrica_repo, app_name)
            proveedor = get_proveedor_for_aplicacion(proveedor_repo, app_name)

            for repo in repos:
                metrics = calculate_repo_metrics(metrica_repo, historico_repo, app_name, repo)

                daily_record = {
                    'aplicacion': app_name,
                    'repo': repo,
                    'proveedor': proveedor,
                    'created_on': snapshot_date,
                    'num_bugs': metrics['num_bugs'],
                    'num_vulnerabilities': metrics['num_vulnerabilities'],
                    'num_code_smells': metrics['num_code_smells'],
                    'num_quality': metrics['num_quality'],
                    'num_analisis': metrics['num_analisis']
                }
                daily_records.append(daily_record)
                total_repos += 1

        print(f"[OK] Extracted metrics for {total_repos} repositories across {len(aplicaciones)} applications")
        return daily_records


def load_daily_to_db(app, daily_data: List[Dict[str, Any]], batch_size: int = 100):
    """Load daily metrics into daily table.

    Args:
        app: Flask application instance
        daily_data: List of daily metric dictionaries
        batch_size: Batch size for bulk inserts

    Returns:
        Number of records inserted
    """
    with app.app_context():
        print(f"Loading {len(daily_data)} daily records...")
        total_records = len(daily_data)
        records_inserted = 0

        # Process in batches
        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = daily_data[start_idx:end_idx]

            daily_batch = []
            for record in batch:
                daily = Daily(
                    aplicacion=record['aplicacion'],
                    repo=record['repo'],
                    proveedor=record['proveedor'],
                    created_on=record['created_on'],
                    num_bugs=record['num_bugs'],
                    num_vulnerabilities=record['num_vulnerabilities'],
                    num_code_smells=record['num_code_smells'],
                    num_quality=record['num_quality'],
                    num_analisis=record['num_analisis']
                )
                daily_batch.append(daily)

            # Bulk insert
            db.session.bulk_save_objects(daily_batch)
            db.session.commit()

            records_inserted += len(daily_batch)
            progress = (records_inserted / total_records) * 100
            print(f"  Progress: {records_inserted}/{total_records} ({progress:.1f}%)")

        print(f"[OK] Loaded {records_inserted} daily records")
        return records_inserted


def clear_daily_for_date(app, snapshot_date: date):
    """Clear daily records for a specific date.

    Args:
        app: Flask application instance
        snapshot_date: Date to clear

    Returns:
        Number of records deleted
    """
    with app.app_context():
        print(f"Clearing existing daily records for {snapshot_date}...")
        deleted_count = (
            db.session.query(Daily)
            .filter(Daily.created_on == snapshot_date)
            .delete()
        )
        db.session.commit()
        print(f"[OK] Deleted {deleted_count} existing records")
        return deleted_count


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Generate daily metrics snapshots'
    )
    parser.add_argument(
        '--config',
        type=str,
        choices=['Development', 'Production', 'Testing'],
        default='Development',
        help='Configuration environment (default: Development)'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Snapshot date (YYYY-MM-DD, default: today)'
    )
    parser.add_argument(
        '--clear-date',
        action='store_true',
        help='Clear existing records for the date before generating'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for bulk inserts (default: 100)'
    )

    args = parser.parse_args()

    # Parse date
    if args.date:
        try:
            snapshot_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"[ERROR] Invalid date format: {args.date}. Use YYYY-MM-DD")
            return 1
    else:
        snapshot_date = date.today()

    # Get configuration
    config_name = args.config
    config_class = config_dict.get(config_name)

    if not config_class:
        print(f"[ERROR] Invalid configuration: {config_name}")
        return 1

    # Create Flask application
    app = create_app(config_class)

    print("\n" + "="*60)
    print("Daily Metrics Generation Script")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Snapshot date: {snapshot_date}")
    print(f"Clear existing: {args.clear_date}")
    print(f"Batch size: {args.batch_size}")
    print("="*60 + "\n")

    start_time = time.time()

    try:
        # Clear existing records if requested
        if args.clear_date:
            clear_daily_for_date(app, snapshot_date)
            print()

        # Extract daily metrics
        daily_data = extract_daily_metrics(app, snapshot_date)
        print()

        # Load into database
        records_inserted = load_daily_to_db(app, daily_data, args.batch_size)

    except Exception as e:
        print(f"\n[ERROR] Error during daily metrics generation: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    duration = time.time() - start_time
    print("\n" + "="*60)
    print("Daily Metrics Generation Summary")
    print("="*60)
    print(f"Snapshot date: {snapshot_date}")
    print(f"Records generated: {records_inserted}")
    print(f"Duration: {duration:.2f} seconds")
    print("="*60)
    print("\n[OK] Daily metrics generation completed successfully!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
