#!/usr/bin/env python
"""
Statistics Generation Script
============================

Generates aggregated statistics from metricas table and loads them into stats table.

The stats table contains denormalized/aggregated data per application:
- Number of repositories
- Count of "A" ratings (reliability, sqale, security, dloc, coverage)
- Count of "OK" quality gates

Usage:
    python scripts/generate_stats.py [--config CONFIG] [--clear]

Options:
    --config CONFIG    Configuration to use (Development, Production, Testing)
    --clear            Clear existing stats before regenerating
    --batch-size N     Batch size for bulk inserts (default: 100)

Examples:
    # Generate stats (append mode)
    python scripts/generate_stats.py

    # Regenerate all stats (clear + generate)
    python scripts/generate_stats.py --clear

    # Production environment
    python scripts/generate_stats.py --config Production --clear

Created: Post-Phase 10 - Statistics Generation
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import time

# Add project root to Python path
# Script is in scripts/data/, so go up two levels to reach project root
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from infocodest import create_app
from infocodest.extensions import db
from config import config_dict

# Import models
from infocodest.models.stat import Stat
from infocodest.models.metricas import Metrica

# Import repositories
from infocodest.repositories.metrica_repository import MetricaRepository

# Add scripts directory to path for ETL imports
scripts_dir = Path(__file__).parent.parent.absolute()  # Go up to scripts/ directory
sys.path.insert(0, str(scripts_dir))

# Import ETL if available
try:
    from scripts.etl.etl import transformar_stats
    HAS_ETL = True
except ImportError:
    HAS_ETL = False
    print("⚠️  Warning: ETL transformar_stats not found. Stats will not be transformed.")


def get_distinct_aplicaciones(metrica_repo) -> List[str]:
    """Get list of distinct applications from metricas.

    Args:
        metrica_repo: MetricaRepository instance

    Returns:
        List of application names
    """
    return metrica_repo.get_distinct_aplicaciones()


def get_repo_count_by_aplicacion(metrica_repo, aplicacion: str) -> int:
    """Count repositories for a specific application.

    Args:
        metrica_repo: MetricaRepository instance
        aplicacion: Application name

    Returns:
        Number of repositories
    """
    return metrica_repo.count_by_aplicacion(aplicacion)


def get_label_a_count(metrica_repo, aplicacion: str, label_column: str) -> int:
    """Count records with 'A' rating for a specific label column.

    Args:
        metrica_repo: MetricaRepository instance
        aplicacion: Application name
        label_column: Column name (e.g., 'reliability_label')

    Returns:
        Count of 'A' ratings
    """
    # Using SQLAlchemy filter
    count = (
        metrica_repo.session.query(Metrica)
        .filter(
            Metrica.aplicacion == aplicacion,
            getattr(Metrica, label_column) == 'A'
        )
        .count()
    )
    return count


def get_alert_status_ok_count(metrica_repo, aplicacion: str) -> int:
    """Count records with alert_status='OK' for an application.

    Args:
        metrica_repo: MetricaRepository instance
        aplicacion: Application name

    Returns:
        Count of OK status
    """
    count = (
        metrica_repo.session.query(Metrica)
        .filter(
            Metrica.aplicacion == aplicacion,
            Metrica.alert_status == 'OK'
        )
        .count()
    )
    return count


def extract_stats_from_metricas(app) -> List[Dict[str, Any]]:
    """Extract aggregated statistics from metricas table.

    Args:
        app: Flask application instance

    Returns:
        List of dictionaries with stats per application
    """
    with app.app_context():
        metrica_repo = MetricaRepository()

        print("Extracting statistics from metricas table...")
        aplicaciones = get_distinct_aplicaciones(metrica_repo)
        print(f"Found {len(aplicaciones)} applications")

        stats_data = []
        for i, app_name in enumerate(aplicaciones, 1):
            print(f"  Processing {i}/{len(aplicaciones)}: {app_name}")

            stat_record = {
                'aplicacion': app_name,
                'repos': get_repo_count_by_aplicacion(metrica_repo, app_name),
                'reliability_rating': get_label_a_count(metrica_repo, app_name, 'reliability_label'),
                'sqale_rating': get_label_a_count(metrica_repo, app_name, 'sqale_label'),
                'security_rating': get_label_a_count(metrica_repo, app_name, 'security_label'),
                'alert_status_ok': get_alert_status_ok_count(metrica_repo, app_name),
                'dloc_rating': get_label_a_count(metrica_repo, app_name, 'dloc_label'),
                'coverage_rating': get_label_a_count(metrica_repo, app_name, 'coverage_label'),
            }
            stats_data.append(stat_record)

        print(f"✓ Extracted statistics for {len(stats_data)} applications")
        return stats_data


def transform_stats(stats_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform stats data using ETL function.

    Args:
        stats_data: List of stat dictionaries

    Returns:
        Transformed stats data
    """
    if not HAS_ETL:
        print("⚠️  Skipping transformation (ETL not available)")
        # Add default labels
        for stat in stats_data:
            stat['reliability_label'] = 'A' if stat['reliability_rating'] > 0 else 'F'
            stat['sqale_label'] = 'A' if stat['sqale_rating'] > 0 else 'F'
            stat['security_label'] = 'A' if stat['security_rating'] > 0 else 'F'
            stat['alert_status_label'] = 'OK' if stat['alert_status_ok'] > 0 else 'ERROR'
            stat['dloc_label'] = 'A' if stat['dloc_rating'] > 0 else 'F'
            stat['coverage_label'] = 'A' if stat['coverage_rating'] > 0 else 'F'
        return stats_data

    print("Transforming statistics...")
    import pandas as pd
    df_stats = pd.DataFrame(stats_data)
    df_transformed = transformar_stats(df_stats)
    return df_transformed.to_dict('records')


def load_stats_to_db(app, stats_data: List[Dict[str, Any]], batch_size: int = 100):
    """Load statistics into stats table.

    Args:
        app: Flask application instance
        stats_data: List of stat dictionaries
        batch_size: Batch size for bulk inserts

    Returns:
        Number of records inserted
    """
    with app.app_context():
        print(f"Loading {len(stats_data)} statistics records...")
        total_records = len(stats_data)
        records_inserted = 0

        # Process in batches
        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = stats_data[start_idx:end_idx]

            stats_batch = []
            for record in batch:
                stat = Stat(
                    aplicacion=record['aplicacion'],
                    repos=int(record['repos']),
                    reliability_rating=int(record['reliability_rating']),
                    reliability_label=record.get('reliability_label', 'F'),
                    sqale_rating=int(record['sqale_rating']),
                    sqale_label=record.get('sqale_label', 'F'),
                    security_rating=int(record['security_rating']),
                    security_label=record.get('security_label', 'F'),
                    alert_status_ok=int(record['alert_status_ok']),
                    alert_status_label=record.get('alert_status_label', 'ERROR'),
                    dloc_rating=int(record['dloc_rating']),
                    dloc_label=record.get('dloc_label', 'F'),
                    coverage_rating=int(record['coverage_rating']),
                    coverage_label=record.get('coverage_label', 'F')
                )
                stats_batch.append(stat)

            # Bulk insert
            db.session.bulk_save_objects(stats_batch)
            db.session.commit()

            records_inserted += len(stats_batch)
            progress = (records_inserted / total_records) * 100
            print(f"  Progress: {records_inserted}/{total_records} ({progress:.1f}%)")

        print(f"✓ Loaded {records_inserted} statistics records")
        return records_inserted


def clear_stats_table(app):
    """Clear all records from stats table.

    Args:
        app: Flask application instance

    Returns:
        Number of records deleted
    """
    with app.app_context():
        print("Clearing existing statistics...")
        deleted_count = db.session.query(Stat).delete()
        db.session.commit()
        print(f"✓ Deleted {deleted_count} existing records")
        return deleted_count


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Generate aggregated statistics from metricas table'
    )
    parser.add_argument(
        '--config',
        type=str,
        choices=['Development', 'Production', 'Testing'],
        default='Development',
        help='Configuration environment (default: Development)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing stats before regenerating'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for bulk inserts (default: 100)'
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
    print("Statistics Generation Script")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Clear existing: {args.clear}")
    print(f"Batch size: {args.batch_size}")
    print("="*60 + "\n")

    start_time = time.time()

    try:
        # Clear existing stats if requested
        if args.clear:
            clear_stats_table(app)
            print()

        # Extract stats from metricas
        stats_data = extract_stats_from_metricas(app)
        print()

        # Transform stats
        transformed_stats = transform_stats(stats_data)
        print()

        # Load stats into database
        records_inserted = load_stats_to_db(app, transformed_stats, args.batch_size)

    except Exception as e:
        print(f"\n✗ Error during statistics generation: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    duration = time.time() - start_time
    print("\n" + "="*60)
    print("Statistics Generation Summary")
    print("="*60)
    print(f"Records generated: {records_inserted}")
    print(f"Duration: {duration:.2f} seconds")
    print("="*60)
    print("\n✓ Statistics generation completed successfully!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
