#!/usr/bin/env python
"""
Data Loading Script
===================

Loads initial data from CSV files into the database using the modern architecture.

Supports loading:
- Metricas (SonarQube metrics)
- Historico (historical analysis data)
- Proveedor (provider information)

Usage:
    python scripts/load_data.py [--config CONFIG] [--data-dir DIR]

Options:
    --config CONFIG     Configuration to use (Development, Production, Testing)
    --data-dir DIR      Directory containing CSV files (default: ./datos)
    --metricas FILE     Specific metricas CSV file
    --historico FILE    Specific historico CSV file
    --proveedores FILE  Specific proveedores CSV file
    --skip-transform    Skip ETL transformation step
    --batch-size N      Batch size for bulk inserts (default: 1000)

Examples:
    # Load all data from ./datos directory
    python scripts/load_data.py

    # Load specific files
    python scripts/load_data.py --metricas datos/metricas.csv --proveedores datos/proveedores.csv

    # Production with custom data directory
    python scripts/load_data.py --config Production --data-dir /path/to/data

Created: Post-Phase 10 - Data Loading
"""

import sys
import argparse
import os
from pathlib import Path
from typing import List, Dict, Any
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from infocodest import create_app
from infocodest.extensions import db
from config import config_dict

# Import models
from infocodest.models.metricas import Metrica
from infocodest.models.historico import Historico
from infocodest.models.proveedor import Proveedor

# Import ETL utilities
try:
    from scripts.utils.utils import extract_from_csv
    from scripts.etl.etl import transformar_metricas, transformar_historico
    HAS_ETL = True
except ImportError:
    HAS_ETL = False
    print("⚠️  Warning: ETL utilities not found. Use --skip-transform or install dependencies.")


def load_metricas_from_dataframe(app, df_data, batch_size=1000):
    """Load metricas data from pandas DataFrame using SQLAlchemy ORM.

    Args:
        app: Flask application instance
        df_data: Pandas DataFrame with transformed data
        batch_size: Number of records to insert per batch

    Returns:
        int: Number of records inserted
    """
    with app.app_context():
        print("Loading metricas data...")
        total_records = len(df_data)
        records_inserted = 0

        # Process in batches for better performance
        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = df_data.iloc[start_idx:end_idx]

            metricas_batch = []
            for _, row in batch.iterrows():
                metrica = Metrica(
                    repo=str(row["name"]) + "-" + str(row["tipo"]) + "-" + str(row["lenguaje"]),
                    aplicacion=row["aplicacion"],
                    fecha=row["date"],
                    bugs=int(row["bugs"]),
                    reliability_rating=int(row["reliability_rating"]),
                    reliability_label=row["reliability_label"],
                    vulnerabilities=int(row["vulnerabilities"]),
                    security_rating=int(row["security_rating"]),
                    security_label=row["security_label"],
                    code_smells=int(row["code_smells"]),
                    sqale_rating=int(row["sqale_rating"]),
                    sqale_label=row["sqale_label"],
                    alert_status=row["alert_status"],
                    project=row["project"],
                    complexity=int(row["complexity"]),
                    coverage=float(row["coverage"]),
                    unit_tests='N/A',
                    ncloc=int(row["ncloc"]),
                    duplicated_line_density=float(row["duplicated_lines_density"]),
                    sqale_index=int(row["sqale_index"]),
                    sqale_debt_ratio=float(row["sqale_debt_ratio"]),
                    size=row["size"],
                    dloc_label=row["dloc_label"],
                    coverage_label=row["coverage_label"],
                    quality_gate=row["quality_gate"]
                )
                metricas_batch.append(metrica)

            # Bulk insert batch
            db.session.bulk_save_objects(metricas_batch)
            db.session.commit()

            records_inserted += len(metricas_batch)
            progress = (records_inserted / total_records) * 100
            print(f"  Progress: {records_inserted}/{total_records} ({progress:.1f}%)")

        print(f"✓ Loaded {records_inserted} metricas records")
        return records_inserted


def load_historico_from_dataframe(app, df_data, batch_size=1000):
    """Load historico data from pandas DataFrame using SQLAlchemy ORM.

    Args:
        app: Flask application instance
        df_data: Pandas DataFrame with transformed data
        batch_size: Number of records to insert per batch

    Returns:
        int: Number of records inserted
    """
    with app.app_context():
        print("Loading historico data...")
        total_records = len(df_data)
        records_inserted = 0

        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = df_data.iloc[start_idx:end_idx]

            historico_batch = []
            for _, row in batch.iterrows():
                historico = Historico(
                    repo=str(row["name"]) + "-" + str(row["tipo"]) + "-" + str(row["lenguaje"]),
                    aplicacion=row["aplicacion"],
                    fecha=row["date"],
                    bugs=int(row["bugs"]),
                    reliability_rating=int(row["reliability_rating"]),
                    reliability_label=row["reliability_label"],
                    vulnerabilities=int(row["vulnerabilities"]),
                    security_rating=int(row["security_rating"]),
                    security_label=row["security_label"],
                    code_smells=int(row["code_smells"]),
                    sqale_rating=int(row["sqale_rating"]),
                    sqale_label=row["sqale_label"],
                    alert_status=row["alert_status"],
                    project=row["project"],
                    complexity=int(row["complexity"]),
                    coverage=float(row["coverage"]),
                    unit_tests='N/A',
                    ncloc=int(row["ncloc"]),
                    duplicated_line_density=float(row["duplicated_lines_density"]),
                    sqale_index=int(row["sqale_index"]),
                    sqale_debt_ratio=float(row["sqale_debt_ratio"]),
                    size=row["size"],
                    dloc_label=row["dloc_label"],
                    coverage_label=row["coverage_label"],
                    quality_gate=row["quality_gate"]
                )
                historico_batch.append(historico)

            db.session.bulk_save_objects(historico_batch)
            db.session.commit()

            records_inserted += len(historico_batch)
            progress = (records_inserted / total_records) * 100
            print(f"  Progress: {records_inserted}/{total_records} ({progress:.1f}%)")

        print(f"✓ Loaded {records_inserted} historico records")
        return records_inserted


def load_proveedores_from_csv(app, csv_file, batch_size=100):
    """Load proveedores data from CSV file using SQLAlchemy ORM.

    Args:
        app: Flask application instance
        csv_file: Path to proveedores CSV file
        batch_size: Number of records to insert per batch

    Returns:
        int: Number of records inserted
    """
    if not HAS_ETL:
        print("✗ Cannot load proveedores: ETL utilities not available")
        return 0

    with app.app_context():
        print(f"Loading proveedores from {csv_file}...")
        df_data = extract_from_csv(csv_file)
        total_records = len(df_data)
        records_inserted = 0

        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = df_data.iloc[start_idx:end_idx]

            proveedores_batch = []
            for _, row in batch.iterrows():
                proveedor = Proveedor(
                    aplicacion=row["aplicacion"],
                    proveedor=row["proveedor"],
                    tipo=row["tipo"]
                )
                proveedores_batch.append(proveedor)

            db.session.bulk_save_objects(proveedores_batch)
            db.session.commit()

            records_inserted += len(proveedores_batch)
            progress = (records_inserted / total_records) * 100
            print(f"  Progress: {records_inserted}/{total_records} ({progress:.1f}%)")

        print(f"✓ Loaded {records_inserted} proveedor records")
        return records_inserted


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Load data from CSV files into database'
    )
    parser.add_argument(
        '--config',
        type=str,
        choices=['Development', 'Production', 'Testing'],
        default='Development',
        help='Configuration environment (default: Development)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='./datos',
        help='Directory containing CSV files (default: ./datos)'
    )
    parser.add_argument(
        '--metricas',
        type=str,
        help='Specific metricas CSV file'
    )
    parser.add_argument(
        '--historico',
        type=str,
        help='Specific historico CSV file'
    )
    parser.add_argument(
        '--proveedores',
        type=str,
        help='Specific proveedores CSV file'
    )
    parser.add_argument(
        '--skip-transform',
        action='store_true',
        help='Skip ETL transformation (load pre-transformed files)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for bulk inserts (default: 1000)'
    )

    args = parser.parse_args()

    # Check if ETL is required but not available
    if not args.skip_transform and not HAS_ETL:
        print("✗ Error: ETL utilities not available and --skip-transform not specified")
        print("Either:")
        print("  1. Fix ETL imports (check scripts/utils/utils.py and scripts/etl/etl.py)")
        print("  2. Use --skip-transform flag and provide pre-transformed CSV files")
        return 1

    # Get configuration
    config_name = args.config
    config_class = config_dict.get(config_name)

    if not config_class:
        print(f"✗ Invalid configuration: {config_name}")
        return 1

    # Create Flask application
    app = create_app(config_class)

    print("\n" + "="*60)
    print("Data Loading Script")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Data directory: {args.data_dir}")
    print(f"Batch size: {args.batch_size}")
    print("="*60 + "\n")

    total_start_time = time.time()
    stats = {
        'metricas': 0,
        'historico': 0,
        'proveedores': 0
    }

    try:
        # Load metricas
        if args.metricas or os.path.exists(os.path.join(args.data_dir, 'metricas.csv')):
            metricas_file = args.metricas or os.path.join(args.data_dir, 'metricas.csv')

            if args.skip_transform:
                print(f"⚠️  Skipping transformation, loading directly from {metricas_file}")
                # Would need to load directly - not implemented yet
                print("✗ Direct CSV loading not implemented. Use ETL transformation.")
            else:
                start_time = time.time()
                print(f"Transforming metricas from {metricas_file}...")
                df_metricas = transformar_metricas(metricas_file)
                stats['metricas'] = load_metricas_from_dataframe(app, df_metricas, args.batch_size)
                print(f"  Duration: {time.time() - start_time:.2f} seconds\n")

        # Load historico
        if args.historico or os.path.exists(os.path.join(args.data_dir, 'historico.csv')):
            historico_file = args.historico or os.path.join(args.data_dir, 'historico.csv')

            if args.skip_transform:
                print(f"⚠️  Skipping transformation, loading directly from {historico_file}")
                print("✗ Direct CSV loading not implemented. Use ETL transformation.")
            else:
                start_time = time.time()
                print(f"Transforming historico from {historico_file}...")
                df_historico = transformar_historico(historico_file)
                stats['historico'] = load_historico_from_dataframe(app, df_historico, args.batch_size)
                print(f"  Duration: {time.time() - start_time:.2f} seconds\n")

        # Load proveedores
        if args.proveedores or os.path.exists(os.path.join(args.data_dir, 'proveedores.csv')):
            proveedores_file = args.proveedores or os.path.join(args.data_dir, 'proveedores.csv')
            start_time = time.time()
            stats['proveedores'] = load_proveedores_from_csv(app, proveedores_file, args.batch_size)
            print(f"  Duration: {time.time() - start_time:.2f} seconds\n")

    except Exception as e:
        print(f"\n✗ Error during data loading: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    total_duration = time.time() - total_start_time
    print("="*60)
    print("Data Loading Summary")
    print("="*60)
    print(f"Metricas loaded:    {stats['metricas']:>6} records")
    print(f"Historico loaded:   {stats['historico']:>6} records")
    print(f"Proveedores loaded: {stats['proveedores']:>6} records")
    print(f"Total duration:     {total_duration:.2f} seconds")
    print("="*60)
    print("\n✓ Data loading completed successfully!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
