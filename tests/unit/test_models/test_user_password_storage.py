"""
Unit tests for User model password storage.

Tests that passwords are correctly hashed and stored as strings,
compatible with both SQLite and PostgreSQL.
"""

import pytest
from infocodest.models.users import User
from infocodest.utils.security import verify_pass


class TestUserPasswordStorage:
    """Tests for User model password hashing and storage."""

    def test_user_password_is_hashed_on_creation(self):
        """Test that password is automatically hashed when User is created."""
        plain_password = "MySecurePassword123"

        user = User(
            username="testuser",
            email="test@example.com",
            password=plain_password
        )

        # Password should be hashed (not plain text)
        assert user.password != plain_password

        # Password should be a string (not bytes)
        assert isinstance(user.password, str)

    def test_user_password_stored_as_string(self):
        """Test that hashed password is stored as string."""
        user = User(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        # Stored password should be string
        assert isinstance(user.password, str)

        # Should be 192 characters (64 salt + 128 hash, both in hex)
        assert len(user.password) == 192

    def test_user_password_string_length_fits_db_column(self):
        """Test that hashed password fits in String(256) column."""
        user = User(
            username="testuser",
            email="test@example.com",
            password="very_long_password" * 10  # Very long password
        )

        # Hashed password should still be 192 characters
        assert len(user.password) == 192

        # Should fit in VARCHAR(256)
        assert len(user.password) <= 256

    def test_user_password_can_be_verified(self):
        """Test that stored password can be verified."""
        plain_password = "TestPassword456"

        user = User(
            username="testuser",
            email="test@example.com",
            password=plain_password
        )

        # Should be able to verify correct password
        assert verify_pass(plain_password, user.password) is True

        # Should reject wrong password
        assert verify_pass("WrongPassword", user.password) is False

    def test_user_password_with_special_characters(self):
        """Test password with special characters."""
        plain_password = "P@ssw0rd!#$%"

        user = User(
            username="testuser",
            email="test@example.com",
            password=plain_password
        )

        # Should be stored as string
        assert isinstance(user.password, str)

        # Should be verifiable
        assert verify_pass(plain_password, user.password) is True

    def test_user_password_with_unicode(self):
        """Test password with Unicode characters."""
        plain_password = "contraseña_ñ_中文"

        user = User(
            username="testuser",
            email="test@example.com",
            password=plain_password
        )

        # Should be stored as string
        assert isinstance(user.password, str)

        # Should be verifiable
        assert verify_pass(plain_password, user.password) is True

    def test_different_users_different_password_hashes(self):
        """Test that same password for different users produces different hashes."""
        same_password = "SamePassword123"

        user1 = User(
            username="user1",
            email="user1@example.com",
            password=same_password
        )

        user2 = User(
            username="user2",
            email="user2@example.com",
            password=same_password
        )

        # Different users with same password should have different hashes
        # (due to random salts)
        assert user1.password != user2.password

        # But both should verify correctly
        assert verify_pass(same_password, user1.password) is True
        assert verify_pass(same_password, user2.password) is True

    def test_user_password_not_bytes_for_postgresql(self):
        """
        Test that password is NOT bytes (which would cause PostgreSQL error).

        This test validates the fix for:
        psycopg2.errors.StringDataRightTruncation: value too long for type character varying(256)
        """
        user = User(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        # Password MUST be string, not bytes
        assert isinstance(user.password, str)
        assert not isinstance(user.password, bytes)

        # If it were bytes, PostgreSQL would reject it
        # This validates the decode("ascii") call in the model

    def test_user_password_ascii_compatible(self):
        """Test that hashed password is ASCII-compatible."""
        user = User(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        # Should be ASCII (no encoding errors)
        try:
            user.password.encode("ascii")
        except UnicodeEncodeError:
            pytest.fail("Password hash is not ASCII-compatible")

    def test_user_creation_with_kwargs(self):
        """Test User creation using **kwargs (common pattern)."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "is_admin": True
        }

        user = User(**user_data)

        # Password should be hashed
        assert user.password != user_data["password"]
        assert isinstance(user.password, str)

        # Other fields should be set correctly
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_admin is True

        # Password should be verifiable
        assert verify_pass(user_data["password"], user.password) is True


class TestUserPasswordRegressionBugs:
    """Regression tests for specific bugs."""

    def test_password_not_truncated_at_256_chars(self):
        """
        Regression test for: value too long for type character varying(256)

        Before fix: hash_pass() returned bytes, which when passed to PostgreSQL
        as-is would exceed VARCHAR(256) limit.

        After fix: bytes are decoded to ASCII string (192 chars), which fits.
        """
        user = User(
            username="testuser",
            email="test@example.com",
            password="any_password"
        )

        # Password should be exactly 192 characters (fits in VARCHAR(256))
        assert len(user.password) == 192
        assert len(user.password) <= 256

        # Should be string (not bytes)
        assert isinstance(user.password, str)

    def test_password_hash_survives_sqlalchemy_conversion(self):
        """
        Test that password hash survives SQLAlchemy type conversion.

        SQLAlchemy converts types when storing in database.
        This test validates that our string hash works correctly.
        """
        plain_password = "TestPassword"

        user = User(
            username="testuser",
            email="test@example.com",
            password=plain_password
        )

        # Simulate what SQLAlchemy does (converts to string if needed)
        stored_password = str(user.password)

        # Should still be verifiable
        assert verify_pass(plain_password, stored_password) is True
