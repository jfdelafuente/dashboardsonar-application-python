"""
Management CLI for Dashboard SonarQube Application
====================================================

Flask CLI commands for user management, database operations, and utilities.

Commands:
    - create-admin: Create admin user with validation
    - list-users: List all users in the system
    - delete-user: Delete user by email
    - make-admin: Promote user to admin
    - reset-password: Reset user password
    - db-status: Show database connection status
    - seed-data: Load sample data for development

Usage:
    python manage.py <command> [options]

Examples:
    python manage.py create-admin
    python manage.py list-users
    python manage.py delete-user --email user@example.com
"""

import os
import sys
import getpass
import re
from typing import Optional

import click
from flask import Flask
from flask.cli import FlaskGroup, with_appcontext
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from infocodest import create_app
from infocodest.extensions import db
from infocodest.models.users import User
from config import config_dict


# ============================================
# Configuration Selection
# ============================================

def get_config_from_env() -> str:
    """
    Determine configuration based on environment variables.

    Returns:
        Configuration name: 'Development', 'Production', or 'Testing'
    """
    # Check FLASK_ENV first (deprecated but still used)
    flask_env = os.getenv('FLASK_ENV', '').lower()

    # Check DEBUG and TESTING flags
    debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    testing = os.getenv('TESTING', 'False').lower() in ('true', '1', 'yes')

    if testing or flask_env == 'testing':
        return 'Testing'
    elif debug or flask_env == 'development':
        return 'Development'
    else:
        return 'Production'


def create_cli_app(info=None) -> Flask:
    """
    Create Flask app with appropriate configuration for CLI.

    Args:
        info: FlaskGroup info object (unused but required by FlaskGroup)

    Returns:
        Configured Flask application instance
    """
    config_name = get_config_from_env()
    config = config_dict.get(config_name, config_dict['Development'])

    app = create_app(config)

    # Log which config is being used
    click.echo(click.style(f'Using configuration: {config_name}', fg='cyan'))

    return app


# Create FlaskGroup with dynamic configuration
cli = FlaskGroup(create_app=create_cli_app, add_version_option=False)


# ============================================
# Validation Utilities
# ============================================

def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    return True, None


# ============================================
# User Management Commands
# ============================================

@cli.command("create-admin")
@with_appcontext
def create_admin():
    """Create an admin user with email and password validation."""
    click.echo(click.style('\n=== Create Admin User ===\n', fg='green', bold=True))

    # Get and validate email
    while True:
        email = click.prompt('Email address', type=str)

        if not validate_email(email):
            click.echo(click.style('❌ Invalid email format. Please try again.', fg='red'))
            continue

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(click.style(f'❌ User with email {email} already exists.', fg='red'))
            if not click.confirm('Try another email?'):
                return
            continue

        break

    # Get username (optional)
    username = click.prompt('Username (optional, press Enter to skip)',
                           type=str, default='', show_default=False)
    username = username if username else None

    # Get and validate password
    while True:
        password = getpass.getpass('Password: ')
        confirm_password = getpass.getpass('Confirm password: ')

        if password != confirm_password:
            click.echo(click.style('❌ Passwords do not match. Please try again.', fg='red'))
            continue

        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            click.echo(click.style(f'❌ {error_msg}', fg='red'))
            if not click.confirm('Try another password?'):
                return
            continue

        break

    # Create admin user
    try:
        user_data = {
            'email': email,
            'password': password,
            'is_admin': True
        }
        if username:
            user_data['username'] = username

        user = User(**user_data)
        db.session.add(user)
        db.session.commit()

        click.echo(click.style(f'\n✅ Admin user created successfully!', fg='green', bold=True))
        click.echo(f'   Email: {email}')
        if username:
            click.echo(f'   Username: {username}')
        click.echo(f'   Admin: Yes')

    except IntegrityError as e:
        db.session.rollback()
        click.echo(click.style(f'❌ Database error: Email or username already exists.', fg='red'))
        click.echo(click.style(f'   Details: {str(e.orig)}', fg='yellow'))

    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f'❌ Failed to create admin user: {str(e)}', fg='red'))
        raise


@cli.command("list-users")
@with_appcontext
def list_users():
    """List all users in the system."""
    click.echo(click.style('\n=== User List ===\n', fg='cyan', bold=True))

    try:
        users = User.query.order_by(User.created_on.desc()).all()

        if not users:
            click.echo(click.style('No users found in the database.', fg='yellow'))
            return

        click.echo(f'Total users: {len(users)}\n')

        # Table header
        click.echo(click.style(
            f'{"ID":<5} {"Email":<30} {"Username":<20} {"Admin":<8} {"Created":<20}',
            fg='cyan', bold=True
        ))
        click.echo('-' * 85)

        # Table rows
        for user in users:
            admin_badge = click.style('✓ Yes', fg='green') if user.is_admin else 'No'
            username_display = user.username or '-'
            created_display = user.created_on.strftime('%Y-%m-%d %H:%M') if user.created_on else '-'

            click.echo(
                f'{user.id:<5} {user.email:<30} {username_display:<20} '
                f'{admin_badge:<8} {created_display:<20}'
            )

        click.echo()

    except Exception as e:
        click.echo(click.style(f'❌ Failed to list users: {str(e)}', fg='red'))
        raise


@cli.command("delete-user")
@click.option('--email', prompt='Email of user to delete', help='Email address of user to delete')
@with_appcontext
def delete_user(email: str):
    """Delete a user by email address."""
    click.echo(click.style(f'\n=== Delete User: {email} ===\n', fg='yellow', bold=True))

    try:
        user = User.query.filter_by(email=email).first()

        if not user:
            click.echo(click.style(f'❌ User with email {email} not found.', fg='red'))
            return

        # Show user details
        click.echo(f'User ID: {user.id}')
        click.echo(f'Email: {user.email}')
        click.echo(f'Username: {user.username or "-"}')
        click.echo(f'Admin: {"Yes" if user.is_admin else "No"}')
        click.echo()

        # Confirm deletion
        if not click.confirm(click.style('⚠️  Are you sure you want to delete this user?', fg='yellow', bold=True)):
            click.echo('Deletion cancelled.')
            return

        db.session.delete(user)
        db.session.commit()

        click.echo(click.style(f'✅ User {email} deleted successfully.', fg='green'))

    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f'❌ Failed to delete user: {str(e)}', fg='red'))
        raise


@cli.command("make-admin")
@click.option('--email', prompt='Email of user to promote', help='Email address of user')
@with_appcontext
def make_admin(email: str):
    """Promote a user to admin status."""
    click.echo(click.style(f'\n=== Promote User to Admin: {email} ===\n', fg='cyan', bold=True))

    try:
        user = User.query.filter_by(email=email).first()

        if not user:
            click.echo(click.style(f'❌ User with email {email} not found.', fg='red'))
            return

        if user.is_admin:
            click.echo(click.style(f'ℹ️  User {email} is already an admin.', fg='yellow'))
            return

        user.is_admin = True
        db.session.commit()

        click.echo(click.style(f'✅ User {email} promoted to admin successfully.', fg='green'))

    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f'❌ Failed to promote user: {str(e)}', fg='red'))
        raise


@cli.command("reset-password")
@click.option('--email', prompt='Email of user', help='Email address of user')
@with_appcontext
def reset_password(email: str):
    """Reset a user's password."""
    click.echo(click.style(f'\n=== Reset Password: {email} ===\n', fg='cyan', bold=True))

    try:
        user = User.query.filter_by(email=email).first()

        if not user:
            click.echo(click.style(f'❌ User with email {email} not found.', fg='red'))
            return

        # Get and validate new password
        while True:
            password = getpass.getpass('New password: ')
            confirm_password = getpass.getpass('Confirm new password: ')

            if password != confirm_password:
                click.echo(click.style('❌ Passwords do not match. Please try again.', fg='red'))
                continue

            # Validate password strength
            is_valid, error_msg = validate_password_strength(password)
            if not is_valid:
                click.echo(click.style(f'❌ {error_msg}', fg='red'))
                if not click.confirm('Try another password?'):
                    return
                continue

            break

        # Update password (User model will hash it automatically)
        from infocodest.utils.security import hash_pass
        user.password = hash_pass(password).decode('ascii')
        db.session.commit()

        click.echo(click.style(f'✅ Password for {email} reset successfully.', fg='green'))

    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f'❌ Failed to reset password: {str(e)}', fg='red'))
        raise


# ============================================
# Database Utility Commands
# ============================================

@cli.command("db-status")
@with_appcontext
def db_status():
    """Show database connection and status information."""
    click.echo(click.style('\n=== Database Status ===\n', fg='cyan', bold=True))

    try:
        # Get database URI (masked)
        from config.utils import mask_db_uri
        from flask import current_app

        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        masked_uri = mask_db_uri(db_uri)

        click.echo(f'Database URI: {masked_uri}')

        # Test connection
        db.session.execute(db.text('SELECT 1'))
        click.echo(click.style('✅ Database connection: OK', fg='green'))

        # Get user count
        user_count = User.query.count()
        admin_count = User.query.filter_by(is_admin=True).count()

        click.echo(f'\nUsers:')
        click.echo(f'  Total: {user_count}')
        click.echo(f'  Admins: {admin_count}')
        click.echo(f'  Regular: {user_count - admin_count}')

        # Database engine info
        click.echo(f'\nDatabase Engine: {db.engine.name}')
        click.echo(f'SQLAlchemy Version: {db.__version__}')

        click.echo()

    except SQLAlchemyError as e:
        click.echo(click.style('❌ Database connection: FAILED', fg='red'))
        click.echo(click.style(f'   Error: {str(e)}', fg='yellow'))

    except Exception as e:
        click.echo(click.style(f'❌ Failed to get database status: {str(e)}', fg='red'))
        raise


@cli.command("seed-data")
@click.option('--users', default=5, help='Number of test users to create')
@with_appcontext
def seed_data(users: int):
    """
    Load sample data for development/testing.

    Creates test users with predictable credentials.
    """
    click.echo(click.style('\n=== Seed Sample Data ===\n', fg='cyan', bold=True))

    if not click.confirm(f'⚠️  This will create {users} test users. Continue?'):
        click.echo('Seed cancelled.')
        return

    try:
        created_count = 0

        # Create test admin
        admin_email = 'admin@test.com'
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                username='admin',
                password='Admin123!',
                is_admin=True
            )
            db.session.add(admin)
            created_count += 1
            click.echo(f'✅ Created admin: {admin_email} (password: Admin123!)')

        # Create test users
        for i in range(1, users):
            email = f'user{i}@test.com'
            if not User.query.filter_by(email=email).first():
                user = User(
                    email=email,
                    username=f'user{i}',
                    password='User123!',
                    is_admin=False
                )
                db.session.add(user)
                created_count += 1

        db.session.commit()

        click.echo(click.style(f'\n✅ Seed completed! Created {created_count} users.', fg='green', bold=True))
        click.echo(click.style('\n⚠️  WARNING: These are TEST credentials. Do NOT use in production!', fg='yellow'))

    except IntegrityError:
        db.session.rollback()
        click.echo(click.style('⚠️  Some users already exist. Skipped duplicates.', fg='yellow'))

    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f'❌ Failed to seed data: {str(e)}', fg='red'))
        raise


# ============================================
# Help Command
# ============================================

@cli.command("commands")
def list_commands():
    """List all available management commands."""
    click.echo(click.style('\n=== Available Management Commands ===\n', fg='cyan', bold=True))

    commands = [
        ('create-admin', 'Create an admin user with validation'),
        ('list-users', 'List all users in the system'),
        ('delete-user', 'Delete a user by email'),
        ('make-admin', 'Promote a user to admin status'),
        ('reset-password', 'Reset a user\'s password'),
        ('db-status', 'Show database connection status'),
        ('seed-data', 'Load sample data for development'),
        ('commands', 'Show this help message'),
    ]

    for cmd, description in commands:
        click.echo(click.style(f'{cmd:<20}', fg='green') + description)

    click.echo(click.style('\nFlask built-in commands:', fg='cyan'))
    click.echo(click.style('db init            ', fg='green') + 'Initialize migrations')
    click.echo(click.style('db migrate         ', fg='green') + 'Create migration')
    click.echo(click.style('db upgrade         ', fg='green') + 'Apply migrations')
    click.echo(click.style('db downgrade       ', fg='green') + 'Revert migrations')
    click.echo(click.style('routes             ', fg='green') + 'Show all routes')
    click.echo(click.style('shell              ', fg='green') + 'Start interactive shell')

    click.echo(click.style('\nUsage:', fg='cyan'))
    click.echo('  python manage.py <command> [options]')
    click.echo('\nExamples:')
    click.echo('  python manage.py create-admin')
    click.echo('  python manage.py list-users')
    click.echo('  python manage.py delete-user --email user@example.com')
    click.echo()


# ============================================
# Entry Point
# ============================================

if __name__ == "__main__":
    cli()
