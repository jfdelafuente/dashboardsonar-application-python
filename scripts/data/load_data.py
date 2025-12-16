#!/usr/bin/env python
"""
Data Loading Script
===================

Loads initial data from CSV files into the database using the modern architecture.

Supports loading:
- Metricas (SonarQube metrics)
- Historico (historical analysis data)
- Proveedor (provider information)

Configuration:
    Default filenames and data directory can be configured via environment variables:
    - DATA_DIR: Directory containing CSV files (default: ./datos)
    - METRICAS_FILENAME: Metricas CSV filename (default: metricas.csv)
    - HISTORICO_FILENAME: Historico CSV filename (default: historico.csv)
    - PROVEEDORES_FILENAME: Proveedores CSV filename (default: proveedores.csv)

Usage:
    python scripts/data/load_data.py [--config CONFIG] [--data-dir DIR]

Options:
    --config CONFIG     Configuration to use (Development, Production, Testing)
    --data-dir DIR      Directory containing CSV files (overrides config)
    --metricas FILE     Specific metricas CSV file (overrides config)
    --historico FILE    Specific historico CSV file (overrides config)
    --proveedores FILE  Specific proveedores CSV file (overrides config)
    --skip-transform    Skip ETL transformation step
    --batch-size N      Batch size for bulk inserts (default: 1000)

Examples:
    # Load all data using config defaults
    python scripts/data/load_data.py

    # Load with custom data directory
    python scripts/data/load_data.py --data-dir /path/to/data

    # Load specific files
    python scripts/data/load_data.py --metricas datos/custom_metricas.csv

    # Production with environment variables
    export DATA_DIR=/production/data
    export METRICAS_FILENAME=prod_metricas.csv
    python scripts/data/load_data.py --config Production

Created: Post-Phase 10 - Data Loading
Updated: Configuration system - Add configurable filenames
"""

import sys
import argparse
import os
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
from infocodest.models.metricas import Metrica
from infocodest.models.historico import Historico
from infocodest.models.proveedor import Proveedor

# Add scripts directory to path for ETL imports
scripts_dir = Path(__file__).parent.parent.absolute()  # Go up to scripts/ directory
sys.path.insert(0, str(scripts_dir))

# Import ETL utilities
try:
    from utils.utils import extract_from_csv
    from etl.etl import transformar_metricas, transformar_historico
    HAS_ETL = True
except ImportError as e:
    HAS_ETL = False
    print("Warning: ETL utilities not found. Use --skip-transform or install dependencies.")
    print(f"Import error: {e}")


# Field size limits based on model definitions
FIELD_LIMITS = {
    'string': 64,  # Default String(64) from models
    'int_max': 2147483647,  # Max value for Integer (32-bit)
    'int_min': -2147483648,  # Min value for Integer (32-bit)
}


def validate_string_field(value, field_name, max_length=64):
    """
    Validate and truncate string fields if necessary.

    Args:
        value: Value to validate
        field_name: Name of the field for logging
        max_length: Maximum allowed length

    Returns:
        Validated/truncated string value
    """
    if value is None:
        return None

    str_value = str(value)
    if len(str_value) > max_length:
        print(f"  Warning: Field '{field_name}' exceeds max length ({len(str_value)} > {max_length}). Truncating.")
        return str_value[:max_length]
    return str_value


def validate_int_field(value, field_name):
    """
    Validate integer fields are within bounds.

    Args:
        value: Value to validate
        field_name: Name of the field for logging

    Returns:
        Validated integer value or None if invalid
    """
    try:
        int_value = int(value)
        if int_value > FIELD_LIMITS['int_max'] or int_value < FIELD_LIMITS['int_min']:
            print(f"  Warning: Field '{field_name}' out of bounds ({int_value}). Setting to 0.")
            return 0
        return int_value
    except (ValueError, TypeError):
        print(f"  Warning: Field '{field_name}' is not a valid integer. Setting to 0.")
        return 0


def validate_float_field(value, field_name):
    """
    Validate float fields.

    Args:
        value: Value to validate
        field_name: Name of the field for logging

    Returns:
        Validated float value or 0.0 if invalid
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"  Warning: Field '{field_name}' is not a valid float. Setting to 0.0.")
        return 0.0


def validate_metrica_record(row, row_index):
    """
    Validate a metrica record and return validated data or None if invalid.

    Args:
        row: DataFrame row
        row_index: Index of the row for logging

    Returns:
        Dict with validated fields or None if record should be skipped
    """
    try:
        # Validate required fields first
        name = validate_string_field(row.get("name"), "name")
        tipo = validate_string_field(row.get("tipo"), "tipo")
        lenguaje = validate_string_field(row.get("lenguaje"), "lenguaje")

        if not name or not tipo or not lenguaje:
            print(f"  Error: Row {row_index} missing required fields (name/tipo/lenguaje). Skipping.")
            return None

        # Build repo field
        repo = f"{name}-{tipo}-{lenguaje}"
        if len(repo) > 64:
            print(f"  Error: Row {row_index} repo field too long ({len(repo)} > 64). Skipping.")
            return None

        # Validate all fields
        return {
            'repo': repo,
            'aplicacion': validate_string_field(row.get("aplicacion"), "aplicacion"),
            'fecha': validate_string_field(row.get("date"), "fecha"),
            'bugs': validate_int_field(row.get("bugs"), "bugs"),
            'reliability_rating': validate_int_field(row.get("reliability_rating"), "reliability_rating"),
            'reliability_label': validate_string_field(row.get("reliability_label"), "reliability_label"),
            'vulnerabilities': validate_int_field(row.get("vulnerabilities"), "vulnerabilities"),
            'security_rating': validate_int_field(row.get("security_rating"), "security_rating"),
            'security_label': validate_string_field(row.get("security_label"), "security_label"),
            'code_smells': validate_int_field(row.get("code_smells"), "code_smells"),
            'sqale_rating': validate_int_field(row.get("sqale_rating"), "sqale_rating"),
            'sqale_label': validate_string_field(row.get("sqale_label"), "sqale_label"),
            'alert_status': validate_string_field(row.get("alert_status"), "alert_status"),
            'project': validate_string_field(row.get("project"), "project"),
            'complexity': validate_int_field(row.get("complexity"), "complexity"),
            'coverage': validate_float_field(row.get("coverage"), "coverage"),
            'unit_tests': 'N/A',
            'ncloc': validate_int_field(row.get("ncloc"), "ncloc"),
            'duplicated_line_density': validate_float_field(row.get("duplicated_lines_density"), "duplicated_line_density"),
            'sqale_index': validate_int_field(row.get("sqale_index"), "sqale_index"),
            'sqale_debt_ratio': validate_float_field(row.get("sqale_debt_ratio"), "sqale_debt_ratio"),
            'size': validate_string_field(row.get("size"), "size"),
            'dloc_label': validate_string_field(row.get("dloc_label"), "dloc_label"),
            'coverage_label': validate_string_field(row.get("coverage_label"), "coverage_label"),
            'quality_gate': validate_string_field(row.get("quality_gate"), "quality_gate"),
        }
    except Exception as e:
        print(f"  Error: Row {row_index} validation failed: {e}. Skipping.")
        return None


def validate_historico_record(row, row_index):
    """
    Validate a historico record and return validated data or None if invalid.

    Args:
        row: DataFrame row
        row_index: Index of the row for logging

    Returns:
        Dict with validated fields or None if record should be skipped
    """
    # Historico has same structure as Metrica, reuse validation
    return validate_metrica_record(row, row_index)


def validate_proveedor_record(row, row_index):
    """
    Validate a proveedor record and return validated data or None if invalid.

    Args:
        row: DataFrame row
        row_index: Index of the row for logging

    Returns:
        Dict with validated fields or None if record should be skipped
    """
    try:
        # Validate required field (aplicacion is unique and not null)
        aplicacion = validate_string_field(row.get("aplicacion"), "aplicacion")

        if not aplicacion:
            print(f"  Error: Row {row_index} missing required field 'aplicacion'. Skipping.")
            return None

        # proveedor and tipo are Text fields (no length limit) but we still validate they're strings
        proveedor = str(row.get("proveedor")) if row.get("proveedor") is not None else None
        tipo = str(row.get("tipo")) if row.get("tipo") is not None else None

        return {
            'aplicacion': aplicacion,
            'proveedor': proveedor,
            'tipo': tipo,
        }
    except Exception as e:
        print(f"  Error: Row {row_index} validation failed: {e}. Skipping.")
        return None


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
        records_skipped = 0

        # Process in batches for better performance
        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = df_data.iloc[start_idx:end_idx]

            metricas_batch = []
            for idx, row in batch.iterrows():
                # Validate record
                validated_data = validate_metrica_record(row, idx)
                if validated_data is None:
                    records_skipped += 1
                    continue

                try:
                    metrica = Metrica(**validated_data)
                    metricas_batch.append(metrica)
                except Exception as e:
                    print(f"  Error: Row {idx} failed to create Metrica object: {e}. Skipping.")
                    records_skipped += 1
                    continue

            # Bulk insert batch
            if metricas_batch:
                try:
                    db.session.bulk_save_objects(metricas_batch)
                    db.session.commit()
                    records_inserted += len(metricas_batch)
                except Exception as e:
                    print(f"  Error: Batch insert failed: {e}. Rolling back and trying individual inserts.")
                    db.session.rollback()

                    # Try inserting records individually
                    for metrica in metricas_batch:
                        try:
                            db.session.add(metrica)
                            db.session.commit()
                            records_inserted += 1
                        except Exception as individual_error:
                            print(f"  Error: Individual insert failed: {individual_error}. Skipping record.")
                            db.session.rollback()
                            records_skipped += 1

            progress = ((records_inserted + records_skipped) / total_records) * 100
            print(f"  Progress: {records_inserted + records_skipped}/{total_records} ({progress:.1f}%) - Inserted: {records_inserted}, Skipped: {records_skipped}")

        print(f"✓ Loaded {records_inserted} metricas records ({records_skipped} skipped)")
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
        records_skipped = 0

        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = df_data.iloc[start_idx:end_idx]

            historico_batch = []
            for idx, row in batch.iterrows():
                # Validate record
                validated_data = validate_historico_record(row, idx)
                if validated_data is None:
                    records_skipped += 1
                    continue

                try:
                    historico = Historico(**validated_data)
                    historico_batch.append(historico)
                except Exception as e:
                    print(f"  Error: Row {idx} failed to create Historico object: {e}. Skipping.")
                    records_skipped += 1
                    continue

            # Bulk insert batch
            if historico_batch:
                try:
                    db.session.bulk_save_objects(historico_batch)
                    db.session.commit()
                    records_inserted += len(historico_batch)
                except Exception as e:
                    print(f"  Error: Batch insert failed: {e}. Rolling back and trying individual inserts.")
                    db.session.rollback()

                    # Try inserting records individually
                    for historico in historico_batch:
                        try:
                            db.session.add(historico)
                            db.session.commit()
                            records_inserted += 1
                        except Exception as individual_error:
                            print(f"  Error: Individual insert failed: {individual_error}. Skipping record.")
                            db.session.rollback()
                            records_skipped += 1

            progress = ((records_inserted + records_skipped) / total_records) * 100
            print(f"  Progress: {records_inserted + records_skipped}/{total_records} ({progress:.1f}%) - Inserted: {records_inserted}, Skipped: {records_skipped}")

        print(f"✓ Loaded {records_inserted} historico records ({records_skipped} skipped)")
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
        records_skipped = 0

        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch = df_data.iloc[start_idx:end_idx]

            proveedores_batch = []
            for idx, row in batch.iterrows():
                # Validate record
                validated_data = validate_proveedor_record(row, idx)
                if validated_data is None:
                    records_skipped += 1
                    continue

                try:
                    proveedor = Proveedor(**validated_data)
                    proveedores_batch.append(proveedor)
                except Exception as e:
                    print(f"  Error: Row {idx} failed to create Proveedor object: {e}. Skipping.")
                    records_skipped += 1
                    continue

            # Bulk insert batch
            if proveedores_batch:
                try:
                    db.session.bulk_save_objects(proveedores_batch)
                    db.session.commit()
                    records_inserted += len(proveedores_batch)
                except Exception as e:
                    print(f"  Error: Batch insert failed: {e}. Rolling back and trying individual inserts.")
                    db.session.rollback()

                    # Try inserting records individually
                    for proveedor in proveedores_batch:
                        try:
                            db.session.add(proveedor)
                            db.session.commit()
                            records_inserted += 1
                        except Exception as individual_error:
                            print(f"  Error: Individual insert failed: {individual_error}. Skipping record.")
                            db.session.rollback()
                            records_skipped += 1

            progress = ((records_inserted + records_skipped) / total_records) * 100
            print(f"  Progress: {records_inserted + records_skipped}/{total_records} ({progress:.1f}%) - Inserted: {records_inserted}, Skipped: {records_skipped}")

        print(f"✓ Loaded {records_inserted} proveedor records ({records_skipped} skipped)")
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
        default=None,  # Will use config value if not specified
        help='Directory containing CSV files (default: from config or ./datos)'
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

    # Get data directory from config if not specified
    data_dir = args.data_dir or app.config.get('DATA_DIR', './datos')

    # Get default filenames from config
    metricas_filename = app.config.get('METRICAS_FILENAME', 'metricas.csv')
    historico_filename = app.config.get('HISTORICO_FILENAME', 'historico.csv')
    proveedores_filename = app.config.get('PROVEEDORES_FILENAME', 'proveedores.csv')

    print("\n" + "="*60)
    print("Data Loading Script")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Data directory: {data_dir}")
    print(f"Default filenames:")
    print(f"  - Metricas: {metricas_filename}")
    print(f"  - Historico: {historico_filename}")
    print(f"  - Proveedores: {proveedores_filename}")
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
        if args.metricas or os.path.exists(os.path.join(data_dir, metricas_filename)):
            metricas_file = args.metricas or os.path.join(data_dir, metricas_filename)

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
        if args.historico or os.path.exists(os.path.join(data_dir, historico_filename)):
            historico_file = args.historico or os.path.join(data_dir, historico_filename)

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
        if args.proveedores or os.path.exists(os.path.join(data_dir, proveedores_filename)):
            proveedores_file = args.proveedores or os.path.join(data_dir, proveedores_filename)
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
