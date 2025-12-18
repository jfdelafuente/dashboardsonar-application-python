"""
Unit tests for security utilities (password hashing and verification).

Tests cover:
- Password hashing functionality
- Password verification (both correct and incorrect passwords)
- Compatibility between SQLite (str) and PostgreSQL (bytes) storage
- Edge cases (empty passwords, special characters, Unicode, very long passwords)
- Security properties (unique salts, hash consistency)

Updated: Priority 3 - Added pytest markers
"""

import pytest
from infocodest.utils.security import hash_pass, verify_pass

# Mark all tests in this module as unit, utils, and security tests
pytestmark = [pytest.mark.unit, pytest.mark.utils, pytest.mark.security]


class TestHashPass:
    """Tests for hash_pass function."""

    def test_hash_pass_returns_bytes(self):
        """Test that hash_pass returns bytes."""
        password = "test_password"
        hashed = hash_pass(password)

        assert isinstance(hashed, bytes)

    def test_hash_pass_returns_correct_length(self):
        """Test that hash_pass returns correct length (64 bytes salt + 128 bytes hash = 192)."""
        password = "test_password"
        hashed = hash_pass(password)

        # Salt: 64 bytes (SHA256 hex) + Hash: 128 bytes (PBKDF2-HMAC-SHA512 hex) = 192 bytes
        assert len(hashed) == 192

    def test_hash_pass_generates_unique_salts(self):
        """Test that hash_pass generates different salts for same password."""
        password = "same_password"
        hash1 = hash_pass(password)
        hash2 = hash_pass(password)

        # Different salts mean different hashes even for same password
        assert hash1 != hash2

        # First 64 bytes are the salt
        salt1 = hash1[:64]
        salt2 = hash2[:64]
        assert salt1 != salt2

    def test_hash_pass_with_empty_password(self):
        """Test hashing empty password."""
        password = ""
        hashed = hash_pass(password)

        assert isinstance(hashed, bytes)
        assert len(hashed) == 192

    def test_hash_pass_with_special_characters(self):
        """Test hashing password with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_pass(password)

        assert isinstance(hashed, bytes)
        assert len(hashed) == 192

    def test_hash_pass_with_unicode_characters(self):
        """Test hashing password with Unicode characters."""
        password = "contraseña_ñ_español_中文_日本語"
        hashed = hash_pass(password)

        assert isinstance(hashed, bytes)
        assert len(hashed) == 192

    def test_hash_pass_with_very_long_password(self):
        """Test hashing very long password (1000 characters)."""
        password = "a" * 1000
        hashed = hash_pass(password)

        assert isinstance(hashed, bytes)
        assert len(hashed) == 192

    def test_hash_pass_with_whitespace(self):
        """Test hashing password with whitespace."""
        password = "  password with spaces  "
        hashed = hash_pass(password)

        # Should hash the password as-is (including spaces)
        assert isinstance(hashed, bytes)
        assert len(hashed) == 192

        # Different from trimmed version
        hashed_trimmed = hash_pass(password.strip())
        # Can't compare directly due to random salts, but verify they hash differently
        # by verifying the trimmed password doesn't match the original hash
        assert not verify_pass(password.strip(), hashed)


class TestVerifyPass:
    """Tests for verify_pass function."""

    def test_verify_pass_correct_password_bytes(self):
        """Test verifying correct password when stored as bytes (PostgreSQL scenario)."""
        password = "correct_password"
        hashed = hash_pass(password)

        # Stored as bytes (like PostgreSQL binary column)
        assert verify_pass(password, hashed) is True

    def test_verify_pass_correct_password_string(self):
        """Test verifying correct password when stored as string (SQLite scenario)."""
        password = "correct_password"
        hashed = hash_pass(password)

        # Convert to string (like SQLite text column)
        hashed_str = hashed.decode("ascii")
        assert verify_pass(password, hashed_str) is True

    def test_verify_pass_incorrect_password_bytes(self):
        """Test verifying incorrect password (bytes storage)."""
        password = "correct_password"
        hashed = hash_pass(password)

        assert verify_pass("wrong_password", hashed) is False

    def test_verify_pass_incorrect_password_string(self):
        """Test verifying incorrect password (string storage)."""
        password = "correct_password"
        hashed = hash_pass(password)
        hashed_str = hashed.decode("ascii")

        assert verify_pass("wrong_password", hashed_str) is False

    def test_verify_pass_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "Password123"
        hashed = hash_pass(password)

        assert verify_pass("Password123", hashed) is True
        assert verify_pass("password123", hashed) is False
        assert verify_pass("PASSWORD123", hashed) is False

    def test_verify_pass_with_empty_password(self):
        """Test verifying empty password."""
        password = ""
        hashed = hash_pass(password)

        assert verify_pass("", hashed) is True
        assert verify_pass("nonempty", hashed) is False

    def test_verify_pass_with_special_characters(self):
        """Test verifying password with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_pass(password)

        assert verify_pass(password, hashed) is True
        assert verify_pass("p@ssw0rd", hashed) is False

    def test_verify_pass_with_unicode(self):
        """Test verifying password with Unicode characters."""
        password = "contraseña_ñ_español"
        hashed = hash_pass(password)

        assert verify_pass(password, hashed) is True
        assert verify_pass("contrasena_n_espanol", hashed) is False

    def test_verify_pass_whitespace_matters(self):
        """Test that whitespace in password matters."""
        password = "password"
        hashed = hash_pass(password)

        assert verify_pass("password", hashed) is True
        assert verify_pass(" password", hashed) is False
        assert verify_pass("password ", hashed) is False
        assert verify_pass(" password ", hashed) is False

    def test_verify_pass_very_long_password(self):
        """Test verifying very long password."""
        password = "a" * 1000
        hashed = hash_pass(password)

        assert verify_pass(password, hashed) is True
        assert verify_pass("a" * 999, hashed) is False
        assert verify_pass("a" * 1001, hashed) is False


class TestPasswordCompatibilitySQLitePostgreSQL:
    """Tests for compatibility between SQLite and PostgreSQL storage."""

    def test_bytes_to_string_to_bytes_roundtrip(self):
        """Test that password hash survives bytes->string->bytes conversion."""
        password = "test_password"
        hashed_bytes = hash_pass(password)

        # Convert to string (like SQLite storage)
        hashed_str = hashed_bytes.decode("ascii")

        # Convert back to bytes (like reading from SQLite and sending to PostgreSQL)
        hashed_bytes_again = hashed_str.encode("ascii")

        # Should still verify
        assert verify_pass(password, hashed_bytes_again) is True

    def test_verify_with_string_from_sqlite(self):
        """Test verifying password stored as string in SQLite."""
        password = "sqlite_password"
        hashed = hash_pass(password)

        # Simulate SQLite storage (stores as string)
        stored_in_sqlite = hashed.decode("ascii")

        # Verify should work with string
        assert verify_pass(password, stored_in_sqlite) is True

    def test_verify_with_bytes_from_postgresql(self):
        """Test verifying password stored as bytes in PostgreSQL."""
        password = "postgresql_password"
        hashed = hash_pass(password)

        # Simulate PostgreSQL storage (stores as bytes)
        stored_in_postgresql = hashed

        # Verify should work with bytes
        assert verify_pass(password, stored_in_postgresql) is True

    def test_same_password_different_databases(self):
        """Test that same password can be verified from both database types."""
        password = "shared_password"
        hashed = hash_pass(password)

        # Store in both formats
        sqlite_format = hashed.decode("ascii")
        postgresql_format = hashed

        # Both should verify correctly
        assert verify_pass(password, sqlite_format) is True
        assert verify_pass(password, postgresql_format) is True


class TestPasswordSecurityProperties:
    """Tests for security properties of password hashing."""

    def test_salt_randomness(self):
        """Test that salts are random (non-deterministic)."""
        password = "same_password"

        # Generate 10 hashes
        hashes = [hash_pass(password) for _ in range(10)]

        # All should be unique
        assert len(set(hashes)) == 10

    def test_hash_consistency_with_same_salt(self):
        """Test that same password + same salt produces same hash."""
        password = "test_password"
        hashed = hash_pass(password)

        # Extract salt (first 64 bytes)
        salt = hashed[:64]

        # Verify uses the same salt from the hash, so it should match
        assert verify_pass(password, hashed) is True

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = hash_pass(password1)
        hash2 = hash_pass(password2)

        # Different passwords should have different hashes
        # (even with potentially same salt, which is astronomically unlikely)
        assert hash1 != hash2

    def test_similar_passwords_different_hashes(self):
        """Test that similar passwords produce different hashes."""
        password1 = "password"
        password2 = "password1"

        hash1 = hash_pass(password1)
        hash2 = hash_pass(password2)

        # Even one character difference should produce completely different hash
        assert hash1 != hash2

    def test_no_password_leakage_in_hash(self):
        """Test that password is not recoverable from hash (one-way function)."""
        password = "secret_password"
        hashed = hash_pass(password)

        # Hash should not contain the original password
        assert password.encode("utf-8") not in hashed
        assert password.encode("ascii") not in hashed

        # Decoded hash should not contain password either
        hashed_str = hashed.decode("ascii")
        assert password not in hashed_str


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_hash_pass_with_newlines(self):
        """Test hashing password with newline characters."""
        password = "pass\nword\n"
        hashed = hash_pass(password)

        assert verify_pass(password, hashed) is True
        assert verify_pass("password", hashed) is False

    def test_hash_pass_with_tabs(self):
        """Test hashing password with tab characters."""
        password = "pass\tword"
        hashed = hash_pass(password)

        assert verify_pass(password, hashed) is True
        assert verify_pass("pass word", hashed) is False

    def test_verify_pass_with_only_salt(self):
        """Test verify_pass with malformed hash (only salt, no hash part)."""
        password = "test"

        # Create a malformed hash (only salt, 64 bytes)
        malformed_hash = b"a" * 64

        # Should not crash, should return False
        assert verify_pass(password, malformed_hash) is False

    def test_hash_pass_with_null_bytes(self):
        """Test hashing password with null bytes."""
        # Note: This is an edge case - passwords with null bytes are unusual
        # but should be handled gracefully
        password = "pass\x00word"
        hashed = hash_pass(password)

        # Should hash without crashing
        assert isinstance(hashed, bytes)
        assert len(hashed) == 192

    def test_numeric_string_password(self):
        """Test hashing purely numeric password."""
        password = "1234567890"
        hashed = hash_pass(password)

        assert verify_pass("1234567890", hashed) is True
        assert verify_pass("0987654321", hashed) is False


class TestPerformance:
    """Tests for performance characteristics (PBKDF2 iterations)."""

    def test_hash_pass_uses_sufficient_iterations(self):
        """Test that hash_pass uses sufficient iterations (100,000)."""
        import hashlib
        import binascii

        password = "test_password"
        hashed = hash_pass(password)

        # Extract salt
        salt = hashed[:64]
        hash_part = hashed[64:]

        # Manually compute hash with 100,000 iterations
        expected_hash = hashlib.pbkdf2_hmac(
            "sha512",
            password.encode("utf-8"),
            salt,
            100000
        )
        expected_hash_hex = binascii.hexlify(expected_hash)

        # Should match
        assert hash_part == expected_hash_hex

    def test_hash_pass_execution_time(self):
        """Test that hash_pass completes in reasonable time (< 1 second)."""
        import time

        password = "test_password"
        start = time.time()
        hash_pass(password)
        duration = time.time() - start

        # Should complete in less than 1 second
        # (100,000 iterations should be fast enough)
        assert duration < 1.0

    def test_verify_pass_execution_time(self):
        """Test that verify_pass completes in reasonable time (< 1 second)."""
        import time

        password = "test_password"
        hashed = hash_pass(password)

        start = time.time()
        verify_pass(password, hashed)
        duration = time.time() - start

        # Should complete in less than 1 second
        assert duration < 1.0


class TestRegressionBugs:
    """Tests for specific bugs that have been fixed."""

    def test_str_decode_attribute_error_fix(self):
        """
        Regression test for: AttributeError: 'str' object has no attribute 'decode'

        This bug occurred when stored_password was already a string (from SQLite)
        and the code tried to call .decode() on it.

        Fixed by adding isinstance() check in verify_pass().
        """
        password = "test_password"
        hashed = hash_pass(password)

        # Simulate SQLite storage (string)
        hashed_str = hashed.decode("ascii")

        # This should NOT raise AttributeError
        result = verify_pass(password, hashed_str)
        assert result is True

    def test_bytes_from_postgresql_still_works(self):
        """
        Regression test to ensure bytes (PostgreSQL) still work after string fix.
        """
        password = "test_password"
        hashed = hash_pass(password)

        # Keep as bytes (PostgreSQL scenario)
        # This should still work
        result = verify_pass(password, hashed)
        assert result is True


class TestIntegration:
    """Integration tests simulating real-world usage scenarios."""

    def test_user_registration_and_login_flow(self):
        """Test complete user registration and login flow."""
        # Registration: user provides password
        user_password = "MySecurePassword123!"

        # System hashes password
        hashed_password = hash_pass(user_password)

        # Simulate storing in database (could be SQLite or PostgreSQL)
        stored_password_sqlite = hashed_password.decode("ascii")  # SQLite
        stored_password_postgresql = hashed_password  # PostgreSQL

        # Login: user provides password again
        login_attempt = "MySecurePassword123!"

        # System verifies password (both storage types should work)
        assert verify_pass(login_attempt, stored_password_sqlite) is True
        assert verify_pass(login_attempt, stored_password_postgresql) is True

        # Wrong password should fail
        wrong_password = "WrongPassword"
        assert verify_pass(wrong_password, stored_password_sqlite) is False
        assert verify_pass(wrong_password, stored_password_postgresql) is False

    def test_database_migration_sqlite_to_postgresql(self):
        """Test migrating password hashes from SQLite to PostgreSQL."""
        password = "user_password"

        # Initially stored in SQLite (as string)
        hashed = hash_pass(password)
        sqlite_stored = hashed.decode("ascii")

        # Verify works in SQLite
        assert verify_pass(password, sqlite_stored) is True

        # Migrate to PostgreSQL (convert back to bytes if needed, or keep as string)
        # PostgreSQL can handle both
        postgresql_stored_as_bytes = sqlite_stored.encode("ascii")
        postgresql_stored_as_string = sqlite_stored

        # Both should work
        assert verify_pass(password, postgresql_stored_as_bytes) is True
        assert verify_pass(password, postgresql_stored_as_string) is True

    def test_password_change_flow(self):
        """Test user changing password."""
        old_password = "OldPassword123"
        new_password = "NewPassword456"

        # Hash old password
        old_hash = hash_pass(old_password)

        # User changes password
        new_hash = hash_pass(new_password)

        # Old password should not work with new hash
        assert verify_pass(old_password, new_hash) is False

        # New password should work with new hash
        assert verify_pass(new_password, new_hash) is True

        # New password should not work with old hash
        assert verify_pass(new_password, old_hash) is False


# Parametrized tests for common scenarios
class TestParametrized:
    """Parametrized tests for comprehensive coverage."""

    @pytest.mark.parametrize("password", [
        "simple",
        "with spaces",
        "with-dash",
        "with_underscore",
        "with.dot",
        "with@at",
        "UPPERCASE",
        "lowercase",
        "MixedCase",
        "123456789",
        "abc123",
        "!@#$%^&*()",
        "emoji😀password",
        "very_long_password_" * 10,
    ])
    def test_hash_and_verify_various_passwords(self, password):
        """Test hash and verify with various password formats."""
        hashed = hash_pass(password)

        # Correct password should verify (both as bytes and string)
        assert verify_pass(password, hashed) is True
        assert verify_pass(password, hashed.decode("ascii")) is True

        # Wrong password should not verify
        assert verify_pass(password + "x", hashed) is False

    @pytest.mark.parametrize("storage_type", ["bytes", "string"])
    def test_verify_with_different_storage_types(self, storage_type):
        """Test verify_pass with different storage types."""
        password = "test_password"
        hashed = hash_pass(password)

        if storage_type == "bytes":
            stored = hashed
        else:  # string
            stored = hashed.decode("ascii")

        assert verify_pass(password, stored) is True
        assert verify_pass("wrong", stored) is False
