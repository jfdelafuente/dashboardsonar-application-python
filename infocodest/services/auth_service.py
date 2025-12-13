"""Service for user authentication and account management.

This module provides business logic for user authentication, registration,
and account operations.
"""

from typing import Optional

from infocodest.repositories.user_repository import UserRepository
from infocodest.models.users import User
from infocodest.models.util import verify_pass


class AuthService:
    """Service for authentication and user account operations.

    This service handles business logic for:
    - User authentication (login validation)
    - User registration
    - Password verification
    - User lookup operations

    Note: This service does NOT handle flask_login session management
    (login_user, logout_user) - those remain in views as they are
    presentation-layer concerns.
    """

    def __init__(self, user_repo: Optional[UserRepository] = None):
        """Initialize AuthService with repository dependencies.

        Args:
            user_repo: Repository for user data (default: new instance)
        """
        self.user_repo = user_repo or UserRepository()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username and password.

        Args:
            username: Username to authenticate
            password: Plain text password to verify

        Returns:
            User entity if authentication successful, None otherwise

        Example:
            >>> service = AuthService()
            >>> user = service.authenticate_user('john', 'password123')
            >>> if user:
            ...     print(f"Authenticated: {user.username}")
            ... else:
            ...     print("Invalid credentials")
        """
        user = self.user_repo.get_by_username(username)

        if user and verify_pass(password, user.password):
            return user

        return None

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        is_admin: bool = False
    ) -> tuple[bool, Optional[User], Optional[str]]:
        """Register a new user account.

        Validates that username and email don't already exist before creating.

        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            is_admin: Whether user should have admin privileges (default: False)

        Returns:
            Tuple of (success, user, error_message)
            - success: True if registration successful, False otherwise
            - user: Created User entity if successful, None otherwise
            - error_message: Error description if failed, None if successful

        Example:
            >>> service = AuthService()
            >>> success, user, error = service.register_user('john', 'john@example.com', 'pass123')
            >>> if success:
            ...     print(f"Created user: {user.username}")
            ... else:
            ...     print(f"Error: {error}")
        """
        # Validate username doesn't exist
        if self.user_repo.username_exists(username):
            return False, None, f"Username '{username}' already exists"

        # Validate email doesn't exist
        if self.user_repo.email_exists(email):
            return False, None, f"Email '{email}' already exists"

        # Create user
        try:
            user = self.user_repo.create_user(
                username=username,
                email=email,
                password=password,
                is_admin=is_admin
            )
            return True, user, None
        except Exception as e:
            return False, None, f"Failed to create user: {str(e)}"

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username to search for

        Returns:
            User entity if found, None otherwise
        """
        return self.user_repo.get_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.

        Args:
            email: Email address to search for

        Returns:
            User entity if found, None otherwise
        """
        return self.user_repo.get_by_email(email)

    def change_password(self, user: User, new_password: str) -> User:
        """Change user's password.

        Args:
            user: User entity to update
            new_password: New plain text password (will be hashed)

        Returns:
            Updated User entity

        Raises:
            SQLAlchemyError: If database operation fails
        """
        return self.user_repo.update_password(user, new_password)

    def validate_username_available(self, username: str) -> bool:
        """Check if username is available for registration.

        Args:
            username: Username to check

        Returns:
            True if username is available, False if already taken
        """
        return not self.user_repo.username_exists(username)

    def validate_email_available(self, email: str) -> bool:
        """Check if email is available for registration.

        Args:
            email: Email address to check

        Returns:
            True if email is available, False if already taken
        """
        return not self.user_repo.email_exists(email)
