"""Repository for User model operations.

This module provides data access methods for user authentication and management.
"""

from typing import Optional
from infocodest.models.users import User
from infocodest.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for managing user accounts.

    This repository provides methods to query and manage user data
    for authentication and authorization.
    """

    def __init__(self):
        """Initialize UserRepository."""
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username to search for

        Returns:
            User entity if found, None otherwise
        """
        return self.find_one(username=username)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.

        Args:
            email: Email address to search for

        Returns:
            User entity if found, None otherwise
        """
        return self.find_one(email=email)

    def get_admins(self) -> list[User]:
        """Get all admin users.

        Returns:
            List of User entities with is_admin=True
        """
        return self.filter_by(is_admin=True)

    def username_exists(self, username: str) -> bool:
        """Check if a username already exists.

        Args:
            username: Username to check

        Returns:
            True if username exists, False otherwise
        """
        return self.exists(username=username)

    def email_exists(self, email: str) -> bool:
        """Check if an email already exists.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        return self.exists(email=email)

    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> User:
        """Create a new user.

        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed automatically by User model)
            is_admin: Whether user should have admin privileges

        Returns:
            Created User entity

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        user = User(
            username=username,
            email=email,
            password=password,
            is_admin=is_admin
        )
        return self.create(user)

    def update_password(self, user: User, new_password: str) -> User:
        """Update user's password.

        Args:
            user: User entity to update
            new_password: New plain text password (will be hashed automatically)

        Returns:
            Updated User entity

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        from infocodest.models.util import hash_pass
        user.password = hash_pass(new_password)
        return self.update(user)

    def promote_to_admin(self, user: User) -> User:
        """Promote a user to admin.

        Args:
            user: User entity to promote

        Returns:
            Updated User entity

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        user.is_admin = True
        return self.update(user)

    def revoke_admin(self, user: User) -> User:
        """Revoke admin privileges from a user.

        Args:
            user: User entity to demote

        Returns:
            Updated User entity

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        user.is_admin = False
        return self.update(user)
