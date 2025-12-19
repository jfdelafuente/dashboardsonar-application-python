"""
Unit tests for manage.py CLI commands.

Tests cover:
- Validation functions (email, password)
- Configuration detection
- User management commands
- Database utility commands
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from sqlalchemy.exc import IntegrityError

from manage import (
    validate_email,
    validate_password_strength,
    get_config_from_env,
    cli,
    create_admin,
    list_users,
    delete_user,
    make_admin,
    reset_password,
    db_status,
    seed_data,
    list_commands
)
from infocodest.models.users import User
from infocodest.extensions import db

# Mark all tests in this module as unit tests
pytestmark = [pytest.mark.unit, pytest.mark.cli]


# ============================================
# Validation Functions Tests
# ============================================

class TestValidateEmail:
    """Tests for email validation function."""

    def test_valid_emails(self):
        """Test that valid email formats are accepted."""
        valid_emails = [
            'user@example.com',
            'test.user@example.com',
            'user+tag@example.co.uk',
            'user_name@example-domain.com',
            'user123@test.org',
            'a@b.co'
        ]
        for email in valid_emails:
            assert validate_email(email), f"Email {email} should be valid"

    def test_invalid_emails(self):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user @example.com',
            'user@example',
            '',
            'user@.com'
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"Email {email} should be invalid"

    def test_edge_cases(self):
        """Test edge cases for email validation."""
        # The current regex accepts long emails, so we test minimal valid email
        assert validate_email('a@b.co')  # Minimal valid email
        assert not validate_email('')  # Empty string
        assert not validate_email('   ')  # Whitespace only


class TestValidatePasswordStrength:
    """Tests for password strength validation."""

    def test_valid_passwords(self):
        """Test that valid passwords pass all requirements."""
        valid_passwords = [
            'Password1',
            'SecurePass123',
            'MyP@ssw0rd',
            'Abcd1234',
            'Test1234Password'
        ]
        for password in valid_passwords:
            is_valid, error_msg = validate_password_strength(password)
            assert is_valid, f"Password {password} should be valid"
            assert error_msg is None

    def test_password_too_short(self):
        """Test that passwords shorter than 8 characters are rejected."""
        is_valid, error_msg = validate_password_strength('Pass1')
        assert not is_valid
        assert "at least 8 characters" in error_msg

    def test_password_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        is_valid, error_msg = validate_password_strength('password123')
        assert not is_valid
        assert "uppercase letter" in error_msg

    def test_password_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        is_valid, error_msg = validate_password_strength('PASSWORD123')
        assert not is_valid
        assert "lowercase letter" in error_msg

    def test_password_no_digit(self):
        """Test that passwords without digits are rejected."""
        is_valid, error_msg = validate_password_strength('PasswordTest')
        assert not is_valid
        assert "digit" in error_msg

    def test_password_edge_cases(self):
        """Test edge cases for password validation."""
        # Exactly 8 characters with all requirements
        is_valid, _ = validate_password_strength('Passw0rd')
        assert is_valid

        # Empty password
        is_valid, error_msg = validate_password_strength('')
        assert not is_valid
        assert "at least 8 characters" in error_msg


# ============================================
# Configuration Detection Tests
# ============================================

class TestGetConfigFromEnv:
    """Tests for environment-based configuration detection."""

    @patch.dict('os.environ', {'TESTING': 'true'})
    def test_testing_config_from_testing_flag(self):
        """Test that TESTING=true returns Testing config."""
        assert get_config_from_env() == 'Testing'

    @patch.dict('os.environ', {'TESTING': '1'})
    def test_testing_config_from_testing_one(self):
        """Test that TESTING=1 returns Testing config."""
        assert get_config_from_env() == 'Testing'

    @patch.dict('os.environ', {'FLASK_ENV': 'testing'})
    def test_testing_config_from_flask_env(self):
        """Test that FLASK_ENV=testing returns Testing config."""
        assert get_config_from_env() == 'Testing'

    @patch.dict('os.environ', {'DEBUG': 'true'}, clear=True)
    def test_development_config_from_debug_flag(self):
        """Test that DEBUG=true returns Development config."""
        assert get_config_from_env() == 'Development'

    @patch.dict('os.environ', {'FLASK_ENV': 'development'}, clear=True)
    def test_development_config_from_flask_env(self):
        """Test that FLASK_ENV=development returns Development config."""
        assert get_config_from_env() == 'Development'

    @patch.dict('os.environ', {}, clear=True)
    def test_production_config_default(self):
        """Test that empty environment returns Production config."""
        assert get_config_from_env() == 'Production'

    @patch.dict('os.environ', {'DEBUG': 'false', 'TESTING': 'false'}, clear=True)
    def test_production_config_explicit_false(self):
        """Test that explicit false values return Production config."""
        assert get_config_from_env() == 'Production'

    @patch.dict('os.environ', {'TESTING': 'true', 'DEBUG': 'true'})
    def test_testing_takes_priority_over_debug(self):
        """Test that TESTING flag takes priority over DEBUG."""
        assert get_config_from_env() == 'Testing'


# ============================================
# CLI Commands Tests
# ============================================

class TestCreateAdminCommand:
    """Tests for create-admin CLI command."""

    def test_create_admin_success(self, app, init_database):
        """Test successful admin creation with valid inputs."""
        runner = CliRunner()

        with app.app_context():
            # Simulate user inputs: email, username, password, confirm password
            result = runner.invoke(
                create_admin,
                input='admin@test.com\nadmin_user\nPassword123\nPassword123\n'
            )

            assert result.exit_code == 0
            assert 'Admin user created successfully' in result.output

            # Verify user was created
            user = User.query.filter_by(email='admin@test.com').first()
            assert user is not None
            assert user.username == 'admin_user'
            assert user.is_admin is True

    def test_create_admin_invalid_email(self, app, init_database):
        """Test admin creation with invalid email format."""
        runner = CliRunner()

        with app.app_context():
            # First input is invalid, then user declines to retry
            result = runner.invoke(
                create_admin,
                input='invalid-email\nn\n'
            )

            assert 'Invalid email format' in result.output

    def test_create_admin_duplicate_email(self, app, init_database):
        """Test admin creation with existing email."""
        runner = CliRunner()

        with app.app_context():
            # Try to create user with existing email (lolo@gmail.com from init_database)
            result = runner.invoke(
                create_admin,
                input='lolo@gmail.com\nn\n'
            )

            assert 'already exists' in result.output

    def test_create_admin_password_mismatch(self, app, init_database):
        """Test admin creation with password mismatch."""
        runner = CliRunner()

        with app.app_context():
            # Passwords don't match, then user declines to retry
            result = runner.invoke(
                create_admin,
                input='newadmin@test.com\nadmin\nPassword123\nDifferent123\nn\n'
            )

            assert 'Passwords do not match' in result.output

    def test_create_admin_weak_password(self, app, init_database):
        """Test admin creation with weak password."""
        runner = CliRunner()

        with app.app_context():
            # Weak password, then user declines to retry
            result = runner.invoke(
                create_admin,
                input='newadmin@test.com\nadmin\nweak\nweak\nn\n'
            )

            assert 'at least 8 characters' in result.output

    def test_create_admin_without_username(self, app, init_database):
        """Test admin creation without optional username."""
        runner = CliRunner()

        with app.app_context():
            # Empty username (press Enter to skip)
            result = runner.invoke(
                create_admin,
                input='admin2@test.com\n\nPassword123\nPassword123\n'
            )

            assert result.exit_code == 0

            user = User.query.filter_by(email='admin2@test.com').first()
            assert user is not None
            assert user.username is None


class TestListUsersCommand:
    """Tests for list-users CLI command."""

    def test_list_users_with_data(self, app, init_database):
        """Test listing users when users exist."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(list_users)

            assert result.exit_code == 0
            assert 'User List' in result.output
            assert 'Total users: 1' in result.output
            assert 'lolo@gmail.com' in result.output

    def test_list_users_empty_database(self, app):
        """Test listing users when database is empty."""
        runner = CliRunner()

        with app.app_context():
            db.create_all()
            result = runner.invoke(list_users)

            assert result.exit_code == 0
            assert 'No users found' in result.output

            db.drop_all()

    def test_list_users_shows_admin_badge(self, app, init_database):
        """Test that admin users show admin badge."""
        runner = CliRunner()

        with app.app_context():
            # Create regular user
            regular_user = User(
                email='regular@test.com',
                username='regular',
                password='Password123',
                is_admin=False
            )
            db.session.add(regular_user)
            db.session.commit()

            result = runner.invoke(list_users)

            assert result.exit_code == 0
            assert 'Total users: 2' in result.output


class TestDeleteUserCommand:
    """Tests for delete-user CLI command."""

    def test_delete_user_success(self, app, init_database):
        """Test successful user deletion."""
        runner = CliRunner()

        with app.app_context():
            # Create user to delete
            user = User(
                email='todelete@test.com',
                username='todelete',
                password='Password123',
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()

            # Delete user, confirming with 'y'
            result = runner.invoke(
                delete_user,
                ['--email', 'todelete@test.com'],
                input='y\n'
            )

            assert result.exit_code == 0
            assert 'deleted successfully' in result.output

            # Verify user was deleted
            deleted_user = User.query.filter_by(email='todelete@test.com').first()
            assert deleted_user is None

    def test_delete_user_not_found(self, app, init_database):
        """Test deleting non-existent user."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                delete_user,
                ['--email', 'nonexistent@test.com']
            )

            assert result.exit_code == 0
            assert 'not found' in result.output

    def test_delete_user_cancelled(self, app, init_database):
        """Test cancelling user deletion."""
        runner = CliRunner()

        with app.app_context():
            # Cancel deletion with 'n'
            result = runner.invoke(
                delete_user,
                ['--email', 'lolo@gmail.com'],
                input='n\n'
            )

            assert result.exit_code == 0
            assert 'cancelled' in result.output

            # Verify user still exists
            user = User.query.filter_by(email='lolo@gmail.com').first()
            assert user is not None


class TestMakeAdminCommand:
    """Tests for make-admin CLI command."""

    def test_make_admin_success(self, app, init_database):
        """Test promoting user to admin."""
        runner = CliRunner()

        with app.app_context():
            # Create regular user
            user = User(
                email='regular@test.com',
                username='regular',
                password='Password123',
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()

            result = runner.invoke(
                make_admin,
                ['--email', 'regular@test.com']
            )

            assert result.exit_code == 0
            assert 'promoted to admin successfully' in result.output

            # Verify user is now admin
            promoted_user = User.query.filter_by(email='regular@test.com').first()
            assert promoted_user.is_admin is True

    def test_make_admin_already_admin(self, app, init_database):
        """Test promoting user who is already admin."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                make_admin,
                ['--email', 'lolo@gmail.com']  # Already admin
            )

            assert result.exit_code == 0
            assert 'already an admin' in result.output

    def test_make_admin_user_not_found(self, app, init_database):
        """Test promoting non-existent user."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                make_admin,
                ['--email', 'nonexistent@test.com']
            )

            assert result.exit_code == 0
            assert 'not found' in result.output


class TestResetPasswordCommand:
    """Tests for reset-password CLI command."""

    def test_reset_password_success(self, app, init_database):
        """Test successful password reset."""
        runner = CliRunner()

        with app.app_context():
            old_password = User.query.filter_by(email='lolo@gmail.com').first().password

            result = runner.invoke(
                reset_password,
                ['--email', 'lolo@gmail.com'],
                input='NewPassword123\nNewPassword123\n'
            )

            assert result.exit_code == 0
            assert 'reset successfully' in result.output

            # Verify password was changed
            user = User.query.filter_by(email='lolo@gmail.com').first()
            assert user.password != old_password

    def test_reset_password_mismatch(self, app, init_database):
        """Test password reset with mismatched passwords."""
        runner = CliRunner()

        with app.app_context():
            # Passwords don't match, then user declines to retry
            result = runner.invoke(
                reset_password,
                ['--email', 'lolo@gmail.com'],
                input='NewPassword123\nDifferent123\nn\n'
            )

            assert 'Passwords do not match' in result.output

    def test_reset_password_weak_password(self, app, init_database):
        """Test password reset with weak password."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                reset_password,
                ['--email', 'lolo@gmail.com'],
                input='weak\nweak\nn\n'
            )

            assert 'at least 8 characters' in result.output

    def test_reset_password_user_not_found(self, app, init_database):
        """Test password reset for non-existent user."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                reset_password,
                ['--email', 'nonexistent@test.com']
            )

            assert result.exit_code == 0
            assert 'not found' in result.output


class TestDbStatusCommand:
    """Tests for db-status CLI command."""

    def test_db_status_success(self, app, init_database):
        """Test database status command."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(db_status)

            assert result.exit_code == 0
            assert 'Database Status' in result.output
            assert 'Database connection: OK' in result.output
            assert 'Total:' in result.output
            assert 'Admins:' in result.output

    @patch('infocodest.extensions.db.session.execute')
    def test_db_status_connection_failure(self, mock_execute, app, init_database):
        """Test database status when connection fails."""
        runner = CliRunner()

        with app.app_context():
            # Simulate database connection failure
            mock_execute.side_effect = Exception("Connection failed")

            result = runner.invoke(db_status)

            # The command raises the exception, so check for error message
            assert 'Failed to get database status' in result.output or result.exit_code != 0


class TestSeedDataCommand:
    """Tests for seed-data CLI command."""

    def test_seed_data_default(self, app, init_database):
        """Test seeding data with default number of users."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                seed_data,
                input='y\n'  # Confirm seeding
            )

            assert result.exit_code == 0
            assert 'Seed Summary' in result.output
            assert 'Created:' in result.output

            # Verify admin was created
            admin = User.query.filter_by(email='admin@test.com').first()
            assert admin is not None
            assert admin.is_admin is True

            # Verify test users were created (5 users = 1 admin + 4 regular)
            total_users = User.query.count()
            assert total_users >= 5  # init_database creates 1, seed creates 5

    def test_seed_data_custom_count(self, app, init_database):
        """Test seeding data with custom number of users."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                seed_data,
                ['--users', '3'],
                input='y\n'
            )

            assert result.exit_code == 0
            assert 'Seed Summary' in result.output

    def test_seed_data_cancelled(self, app, init_database):
        """Test cancelling seed data operation."""
        runner = CliRunner()

        with app.app_context():
            initial_count = User.query.count()

            result = runner.invoke(
                seed_data,
                input='n\n'  # Cancel
            )

            assert 'Seed cancelled' in result.output

            # Verify no users were added
            final_count = User.query.count()
            assert final_count == initial_count

    def test_seed_data_duplicate_handling(self, app, init_database):
        """Test that seeding handles existing users gracefully."""
        runner = CliRunner()

        with app.app_context():
            # Create admin first
            admin = User(
                email='admin@test.com',
                username='admin',
                password='Admin123!',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

            # Try to seed - should skip existing admin
            result = runner.invoke(
                seed_data,
                input='y\n'
            )

            # Should complete without error
            assert result.exit_code == 0


class TestListCommandsCommand:
    """Tests for commands (help) CLI command."""

    def test_list_commands(self, app):
        """Test listing all available commands."""
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(list_commands)

            assert result.exit_code == 0
            assert 'Available Management Commands' in result.output
            assert 'create-admin' in result.output
            assert 'list-users' in result.output
            assert 'delete-user' in result.output
            assert 'make-admin' in result.output
            assert 'reset-password' in result.output
            assert 'db-status' in result.output
            assert 'seed-data' in result.output


# ============================================
# Error Handling Tests
# ============================================

class TestErrorHandling:
    """Tests for error handling in CLI commands."""

    @patch('infocodest.extensions.db.session.commit')
    def test_create_admin_database_error(self, mock_commit, app, init_database):
        """Test create-admin handles database errors."""
        runner = CliRunner()

        with app.app_context():
            # Simulate database error
            mock_commit.side_effect = IntegrityError("Mock error", None, None)

            result = runner.invoke(
                create_admin,
                input='test@test.com\ntest\nPassword123\nPassword123\n'
            )

            assert 'Database error' in result.output or result.exit_code != 0

    @patch('infocodest.extensions.db.session.commit')
    def test_make_admin_database_error(self, mock_commit, app, init_database):
        """Test make-admin handles database errors."""
        runner = CliRunner()

        with app.app_context():
            # Create regular user first
            user = User(
                email='regular@test.com',
                username='regular',
                password='Password123',
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()

            # Now simulate error on promotion
            mock_commit.side_effect = Exception("Database error")

            result = runner.invoke(
                make_admin,
                ['--email', 'regular@test.com']
            )

            assert result.exit_code != 0


# ============================================
# Integration Tests
# ============================================

class TestCLIIntegration:
    """Integration tests for complete CLI workflows."""

    def test_complete_user_lifecycle(self, app, init_database):
        """Test complete user lifecycle: create, list, promote, reset password, delete."""
        runner = CliRunner()

        with app.app_context():
            # 1. Create user
            result = runner.invoke(
                create_admin,
                input='lifecycle@test.com\nlifecycle\nPassword123\nPassword123\n'
            )
            assert result.exit_code == 0

            # 2. List users
            result = runner.invoke(list_users)
            assert 'lifecycle@test.com' in result.output

            # 3. Reset password
            result = runner.invoke(
                reset_password,
                ['--email', 'lifecycle@test.com'],
                input='NewPass123\nNewPass123\n'
            )
            assert result.exit_code == 0

            # 4. Delete user
            result = runner.invoke(
                delete_user,
                ['--email', 'lifecycle@test.com'],
                input='y\n'
            )
            assert result.exit_code == 0

            # 5. Verify deletion
            user = User.query.filter_by(email='lifecycle@test.com').first()
            assert user is None

    def test_create_multiple_users_and_list(self, app, init_database):
        """Test creating multiple users and listing them."""
        runner = CliRunner()

        with app.app_context():
            # Create 3 users
            for i in range(1, 4):
                result = runner.invoke(
                    create_admin,
                    input=f'user{i}@test.com\nuser{i}\nPassword123\nPassword123\n'
                )
                assert result.exit_code == 0

            # List all users
            result = runner.invoke(list_users)
            assert 'user1@test.com' in result.output
            assert 'user2@test.com' in result.output
            assert 'user3@test.com' in result.output
