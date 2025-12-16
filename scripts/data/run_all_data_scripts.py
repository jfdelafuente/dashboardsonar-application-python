#!/usr/bin/env python
"""
Data Pipeline Orchestrator
===========================

Executes all data scripts in the correct order with proper error handling.

This script orchestrates the complete data loading and processing pipeline:
1. load_data.py - Load raw data from CSV files
2. generate_daily.py - Generate daily snapshots
3. generate_stats.py - Generate aggregated statistics
4. generate_registro.py - Create audit registry record

Usage:
    python scripts/data/run_all_data_scripts.py [OPTIONS]

Options:
    --config CONFIG        Configuration to use (Development, Production, Testing)
    --data-dir PATH        Directory containing CSV files (default: ./datos)
    --date DATE            Date for daily snapshot (YYYY-MM-DD, default: today)
    --batch-size N         Batch size for bulk operations (default: 100)
    --clear-daily          Clear existing daily records for the date
    --clear-stats          Clear existing stats before regenerating
    --skip-load            Skip data loading (only run generators)
    --skip-daily           Skip daily generation
    --skip-stats           Skip stats generation
    --skip-registry        Skip registry creation
    --dry-run              Show what would be executed without running

Examples:
    # Full pipeline with defaults
    python scripts/data/run_all_data_scripts.py

    # Production environment, regenerate stats
    python scripts/data/run_all_data_scripts.py --config Production --clear-stats

    # Skip data load, only run generators
    python scripts/data/run_all_data_scripts.py --skip-load

    # Custom data directory and date
    python scripts/data/run_all_data_scripts.py --data-dir ./custom_data --date 2025-12-15

    # Dry run to see execution plan
    python scripts/data/run_all_data_scripts.py --dry-run

Created: 2025-12-16
Author: Dashboard Sonar Team
"""

import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


class DataPipelineOrchestrator:
    """Orchestrates execution of all data processing scripts."""

    def __init__(self, args: argparse.Namespace):
        """
        Initialize orchestrator with command-line arguments.

        Args:
            args: Parsed command-line arguments
        """
        self.args = args
        self.scripts_dir = Path(__file__).parent
        self.project_root = project_root
        self.python_exe = sys.executable

        # Execution results
        self.results: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None

    def load_environment_variables(self):
        """
        Load environment variables from .env file.

        Ensures all scripts have access to database configuration.
        """
        from dotenv import load_dotenv

        env_file = self.project_root / '.env'
        if env_file.exists():
            print(f"[+] Loading environment variables from {env_file}")
            load_dotenv(env_file)
            print("[+] Environment variables loaded successfully")
        else:
            print(f"[!] Warning: .env file not found at {env_file}")
            print("[!] Scripts may fail if database configuration is not set")

    def build_command(self, script_name: str, extra_args: List[str] = None) -> List[str]:
        """
        Build command to execute a script.

        Args:
            script_name: Name of the script file (e.g., "load_data.py")
            extra_args: Additional command-line arguments for the script

        Returns:
            List of command parts for subprocess
        """
        cmd = [self.python_exe, str(self.scripts_dir / script_name)]

        # Add config if specified
        if self.args.config:
            cmd.extend(['--config', self.args.config])

        # Add extra arguments
        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def execute_script(self, script_name: str, extra_args: List[str] = None, description: str = None) -> Dict[str, Any]:
        """
        Execute a data processing script.

        Args:
            script_name: Name of the script file
            extra_args: Additional arguments for the script
            description: Human-readable description of the step

        Returns:
            Dict with execution results (success, returncode, duration, etc.)
        """
        cmd = self.build_command(script_name, extra_args)

        result = {
            'script': script_name,
            'description': description or script_name,
            'command': ' '.join(cmd),
            'success': False,
            'returncode': None,
            'duration': None,
            'error': None
        }

        print(f"\n{'='*80}")
        print(f"[*] Step: {result['description']}")
        print(f"[*] Command: {result['command']}")
        print(f"{'='*80}\n")

        if self.args.dry_run:
            print("[DRY RUN] Would execute command above")
            result['success'] = True
            result['returncode'] = 0
            result['duration'] = 0
            return result

        try:
            start = datetime.now()

            # Execute script and stream output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())

            # Wait for completion
            process.wait()
            end = datetime.now()

            result['returncode'] = process.returncode
            result['duration'] = (end - start).total_seconds()
            result['success'] = process.returncode == 0

            if result['success']:
                print(f"\n[✓] {result['description']} completed successfully ({result['duration']:.2f}s)")
            else:
                print(f"\n[✗] {result['description']} failed with exit code {result['returncode']}")
                result['error'] = f"Exit code {result['returncode']}"

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            print(f"\n[✗] Error executing {script_name}: {e}")

        return result

    def run_load_data(self) -> Dict[str, Any]:
        """Execute load_data.py script."""
        if self.args.skip_load:
            print("\n[SKIP] Data loading skipped (--skip-load)")
            return {'script': 'load_data.py', 'success': True, 'skipped': True}

        extra_args = []

        if self.args.data_dir:
            extra_args.extend(['--data-dir', self.args.data_dir])

        if self.args.batch_size:
            extra_args.extend(['--batch-size', str(self.args.batch_size)])

        return self.execute_script(
            'load_data.py',
            extra_args=extra_args,
            description='1. Load Data from CSV Files'
        )

    def run_generate_daily(self) -> Dict[str, Any]:
        """Execute generate_daily.py script."""
        if self.args.skip_daily:
            print("\n[SKIP] Daily generation skipped (--skip-daily)")
            return {'script': 'generate_daily.py', 'success': True, 'skipped': True}

        extra_args = []

        if self.args.date:
            extra_args.extend(['--date', self.args.date])

        if self.args.clear_daily:
            extra_args.append('--clear-date')

        if self.args.batch_size:
            extra_args.extend(['--batch-size', str(self.args.batch_size)])

        return self.execute_script(
            'generate_daily.py',
            extra_args=extra_args,
            description='2. Generate Daily Snapshots'
        )

    def run_generate_stats(self) -> Dict[str, Any]:
        """Execute generate_stats.py script."""
        if self.args.skip_stats:
            print("\n[SKIP] Stats generation skipped (--skip-stats)")
            return {'script': 'generate_stats.py', 'success': True, 'skipped': True}

        extra_args = []

        if self.args.clear_stats:
            extra_args.append('--clear')

        if self.args.batch_size:
            extra_args.extend(['--batch-size', str(self.args.batch_size)])

        return self.execute_script(
            'generate_stats.py',
            extra_args=extra_args,
            description='3. Generate Aggregated Statistics'
        )

    def run_generate_registro(self) -> Dict[str, Any]:
        """Execute generate_registro.py script."""
        if self.args.skip_registry:
            print("\n[SKIP] Registry creation skipped (--skip-registry)")
            return {'script': 'generate_registro.py', 'success': True, 'skipped': True}

        extra_args = []

        if self.args.date:
            extra_args.extend(['--date', self.args.date])

        # Use custom process name with timestamp
        process_name = f"Data Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        extra_args.extend(['--process-name', process_name])

        return self.execute_script(
            'generate_registro.py',
            extra_args=extra_args,
            description='4. Create Audit Registry Record'
        )

    def print_summary(self):
        """Print execution summary."""
        print(f"\n{'='*80}")
        print("EXECUTION SUMMARY")
        print(f"{'='*80}\n")

        total_duration = (self.end_time - self.start_time).total_seconds()

        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Steps Executed: {len(self.results)}")
        print(f"")

        # Print results table
        success_count = sum(1 for r in self.results if r.get('success', False))
        failed_count = sum(1 for r in self.results if not r.get('success', False) and not r.get('skipped', False))
        skipped_count = sum(1 for r in self.results if r.get('skipped', False))

        print(f"Results:")
        print(f"  ✓ Successful: {success_count}")
        if failed_count > 0:
            print(f"  ✗ Failed:     {failed_count}")
        if skipped_count > 0:
            print(f"  - Skipped:    {skipped_count}")
        print()

        # Detailed results
        print("Details:")
        for result in self.results:
            status = "✓" if result.get('success') else "✗"
            if result.get('skipped'):
                status = "-"

            duration_str = f"{result.get('duration', 0):.2f}s" if result.get('duration') else "skipped"

            print(f"  [{status}] {result['description']:40s} ({duration_str})")

            if result.get('error'):
                print(f"      Error: {result['error']}")

        print(f"\n{'='*80}\n")

        # Exit code based on results
        if failed_count > 0:
            print("[✗] Pipeline completed with errors")
            return 1
        else:
            print("[✓] Pipeline completed successfully")
            return 0

    def run(self) -> int:
        """
        Execute the complete data pipeline.

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print(f"\n{'='*80}")
        print("DATA PIPELINE ORCHESTRATOR")
        print(f"{'='*80}\n")
        print(f"Configuration: {self.args.config or 'Development (default)'}")
        print(f"Data Directory: {self.args.data_dir or './datos (default)'}")
        print(f"Date: {self.args.date or 'today (default)'}")
        print(f"Batch Size: {self.args.batch_size or '100 (default)'}")

        if self.args.dry_run:
            print("\n[DRY RUN MODE] No actual execution")

        # Load environment variables
        self.load_environment_variables()

        # Start execution
        self.start_time = datetime.now()

        # Execute scripts in order
        self.results.append(self.run_load_data())

        # Only continue if previous step succeeded
        if self.results[-1].get('success', False) or self.results[-1].get('skipped', False):
            self.results.append(self.run_generate_daily())

        if self.results[-1].get('success', False) or self.results[-1].get('skipped', False):
            self.results.append(self.run_generate_stats())

        if self.results[-1].get('success', False) or self.results[-1].get('skipped', False):
            self.results.append(self.run_generate_registro())

        self.end_time = datetime.now()

        # Print summary and return exit code
        return self.print_summary()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Data Pipeline Orchestrator - Execute all data scripts in order',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with defaults
  python scripts/data/run_all_data_scripts.py

  # Production environment
  python scripts/data/run_all_data_scripts.py --config Production

  # Regenerate daily and stats
  python scripts/data/run_all_data_scripts.py --clear-daily --clear-stats

  # Custom data directory
  python scripts/data/run_all_data_scripts.py --data-dir ./custom_datos

  # Dry run to see execution plan
  python scripts/data/run_all_data_scripts.py --dry-run
        """
    )

    parser.add_argument(
        '--config',
        choices=['Development', 'Testing', 'Production'],
        help='Configuration to use (default: Development)'
    )

    parser.add_argument(
        '--data-dir',
        type=str,
        help='Directory containing CSV files (default: ./datos)'
    )

    parser.add_argument(
        '--date',
        type=str,
        help='Date for daily snapshot (YYYY-MM-DD, default: today)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        help='Batch size for bulk operations (default: 100)'
    )

    parser.add_argument(
        '--clear-daily',
        action='store_true',
        help='Clear existing daily records for the date before generating'
    )

    parser.add_argument(
        '--clear-stats',
        action='store_true',
        help='Clear existing stats before regenerating'
    )

    parser.add_argument(
        '--skip-load',
        action='store_true',
        help='Skip data loading step'
    )

    parser.add_argument(
        '--skip-daily',
        action='store_true',
        help='Skip daily generation step'
    )

    parser.add_argument(
        '--skip-stats',
        action='store_true',
        help='Skip stats generation step'
    )

    parser.add_argument(
        '--skip-registry',
        action='store_true',
        help='Skip registry creation step'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    orchestrator = DataPipelineOrchestrator(args)
    exit_code = orchestrator.run()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
