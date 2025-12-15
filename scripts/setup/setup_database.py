#!/usr/bin/env python
"""
Database Setup Script
=====================

Initializes the database and creates an admin user.

Usage:
    python scripts/setup/setup_database.py [--config CONFIG]

Options:
    --config CONFIG    Configuration to use (Development, Production, Testing)
                      Default: Development

Examples:
    # Development database with default admin
    python scripts/setup/setup_database.py

    # Production database with custom credentials
    python scripts/setup/setup_database.py --config Production

    # Testing database
    python scripts/setup/setup_database.py --config Testing

Created: Post-Phase 10 - Database Initialization
Updated: Scripts reorganization - Moved to scripts/setup/
"""

import sys
import argparse
from pathlib import Path

# Add project root to Python path
# Script is in scripts/setup/, so go up two levels to reach project root
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from infocodest import create_app
from infocodest.extensions import db
from infocodest.utils.security import hash_pass
from config import config_dict

# Import all models so db.create_all() can find them
from infocodest.models.users import User
from infocodest.models.stat import Stat
from infocodest.models.metricas import Metrica
from infocodest.models.historico import Historico
from infocodest.models.daily import Daily
from infocodest.models.proveedor import Proveedor
from infocodest.models.registros import Registro


def create_tables(app):
    """Create all database tables.

    Args:
        app: Flask application instance

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully")
            return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def create_admin_user(app, username='admin', email='admin@example.com', password='admin123'):
    """Create an admin user.

    Args:
        app: Flask application instance
        username: Admin username (default: 'admin')
        email: Admin email (default: 'admin@example.com')
        password: Admin password (default: 'admin123')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with app.app_context():
            # Check if admin user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"✓ Admin user '{username}' already exists")
                return True

            # Create new admin user
            print(f"Creating admin user '{username}'...")
            admin = User(
                username=username,
                email=email,
                password=password  # User model hashes password in __init__
            )

            db.session.add(admin)
            db.session.commit()

            print(f"✓ Admin user created successfully")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print("\n⚠️  IMPORTANT: Change the default password after first login!")
            return True

    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.session.rollback()
        return False


def get_user_input():
    """Prompt user for admin credentials.

    Returns:
        tuple: (username, email, password)
    """
    print("\n" + "="*60)
    print("Admin User Configuration")
    print("="*60)
    print("Press Enter to use default values shown in [brackets]\n")

    username = input("Username [admin]: ").strip() or 'admin'
    email = input("Email [admin@example.com]: ").strip() or 'admin@example.com'

    # Password input with confirmation
    while True:
        password = input("Password [admin123]: ").strip() or 'admin123'
        password_confirm = input("Confirm password: ").strip() or 'admin123'

        if password == password_confirm:
            break
        else:
            print("✗ Passwords do not match. Please try again.\n")

    return username, email, password


def display_info(config_name, db_uri):
    """Display configuration information.

    Args:
        config_name: Name of the configuration being used
        db_uri: Database URI (masked)
    """
    print("\n" + "="*60)
    print("Database Setup")
    print("="*60)
    print(f"Configuration: {config_name}")
    print(f"Database: {db_uri}")
    print("="*60 + "\n")


def main():
    """Main execution function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Initialize database and create admin user'
    )
    parser.add_argument(
        '--config',
        type=str,
        choices=['Development', 'Production', 'Testing'],
        default='Development',
        help='Configuration environment to use (default: Development)'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run in non-interactive mode with default credentials'
    )
    parser.add_argument(
        '--username',
        type=str,
        default='admin',
        help='Admin username (default: admin)'
    )
    parser.add_argument(
        '--email',
        type=str,
        default='admin@example.com',
        help='Admin email (default: admin@example.com)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default='admin123',
        help='Admin password (default: admin123)'
    )

    args = parser.parse_args()

    # Get configuration
    config_name = args.config
    config_class = config_dict.get(config_name)

    if not config_class:
        print(f"✗ Invalid configuration: {config_name}")
        print(f"Available configurations: {', '.join(config_dict.keys())}")
        return 1

    # Create Flask application
    app = create_app(config_class)

    # Mask password in database URI for display
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    import re
    masked_uri = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', db_uri)

    # Display configuration info
    display_info(config_name, masked_uri)

    # Get admin credentials
    if args.non_interactive:
        username = args.username
        email = args.email
        password = args.password
        print("Running in non-interactive mode with provided credentials\n")
    else:
        username, email, password = get_user_input()

    # Confirm action
    if not args.non_interactive:
        print(f"\nAbout to:")
        print(f"  1. Create/update database tables")
        print(f"  2. Create admin user: {username} ({email})")
        confirm = input("\nContinue? [y/N]: ").strip().lower()

        if confirm != 'y':
            print("Setup cancelled.")
            return 0

    print("\nStarting database setup...\n")

    # Create database tables
    if not create_tables(app):
        return 1

    # Create admin user
    if not create_admin_user(app, username, email, password):
        return 1

    print("\n" + "="*60)
    print("✓ Database setup completed successfully!")
    print("="*60)
    print(f"\nYou can now login with:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print("\n⚠️  Remember to change your password after first login!")
    print("="*60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
