"""
Unit tests for BaseRepository.

Tests generic CRUD operations and query methods of the base repository class.
"""

import pytest
from sqlalchemy.exc import SQLAlchemyError
from infocodest.repositories.base_repository import BaseRepository
from infocodest.models.users import User
from infocodest.extensions import db


class TestBaseRepository:
    """Test suite for BaseRepository CRUD operations."""

    @pytest.fixture
    def user_repo(self, app):
        """Create repository for User model with clean database."""
        with app.app_context():
            db.create_all()
            yield BaseRepository(User)
            db.session.remove()
            db.drop_all()

    def test_create_user(self, user_repo):
        """Test creating a new user."""
        user = User(username='testuser', email='test@example.com', password='password123')
        created = user_repo.create(user)

        assert created.id is not None
        assert created.username == 'testuser'
        assert created.email == 'test@example.com'

    def test_create_user_with_admin_flag(self, user_repo):
        """Test creating an admin user."""
        user = User(username='admin', email='admin@example.com', password='admin123', is_admin=True)
        created = user_repo.create(user)

        assert created.id is not None
        assert created.is_admin is True

    def test_create_many_users(self, user_repo):
        """Test creating multiple users in a single transaction."""
        users = [
            User(username='user1', email='user1@example.com', password='pass1'),
            User(username='user2', email='user2@example.com', password='pass2'),
            User(username='user3', email='user3@example.com', password='pass3'),
        ]
        created_users = user_repo.create_many(users)

        assert len(created_users) == 3
        assert all(user.id is not None for user in created_users)
        assert created_users[0].username == 'user1'
        assert created_users[1].username == 'user2'
        assert created_users[2].username == 'user3'

    def test_get_by_id_existing(self, user_repo):
        """Test retrieving user by ID when it exists."""
        user = User(username='testuser', email='test@example.com', password='password123')
        created = user_repo.create(user)

        retrieved = user_repo.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.username == 'testuser'
        assert retrieved.email == 'test@example.com'

    def test_get_by_id_nonexistent(self, user_repo):
        """Test retrieving non-existent user returns None."""
        result = user_repo.get_by_id(99999)
        assert result is None

    def test_get_all_empty(self, user_repo):
        """Test get_all with no records returns empty list."""
        users = user_repo.get_all()
        assert users == []

    def test_get_all_multiple(self, user_repo):
        """Test get_all with multiple records."""
        user1 = User(username='user1', email='user1@example.com', password='pass1')
        user2 = User(username='user2', email='user2@example.com', password='pass2')
        user3 = User(username='user3', email='user3@example.com', password='pass3')
        user_repo.create(user1)
        user_repo.create(user2)
        user_repo.create(user3)

        users = user_repo.get_all()
        assert len(users) == 3
        usernames = [u.username for u in users]
        assert 'user1' in usernames
        assert 'user2' in usernames
        assert 'user3' in usernames

    def test_update_user(self, user_repo):
        """Test updating user attributes."""
        user = User(username='testuser', email='test@example.com', password='password123')
        created = user_repo.create(user)

        created.username = 'updated_user'
        created.email = 'updated@example.com'
        updated = user_repo.update(created)

        assert updated.username == 'updated_user'
        assert updated.email == 'updated@example.com'

        # Verify update persisted
        retrieved = user_repo.get_by_id(created.id)
        assert retrieved.username == 'updated_user'
        assert retrieved.email == 'updated@example.com'

    def test_delete_user(self, user_repo):
        """Test deleting user."""
        user = User(username='testuser', email='test@example.com', password='password123')
        created = user_repo.create(user)
        user_id = created.id

        user_repo.delete(created)

        retrieved = user_repo.get_by_id(user_id)
        assert retrieved is None

    def test_delete_by_id_existing(self, user_repo):
        """Test deleting user by ID when it exists."""
        user = User(username='testuser', email='test@example.com', password='password123')
        created = user_repo.create(user)
        user_id = created.id

        result = user_repo.delete_by_id(user_id)
        assert result is True

        retrieved = user_repo.get_by_id(user_id)
        assert retrieved is None

    def test_delete_by_id_nonexistent(self, user_repo):
        """Test deleting non-existent user returns False."""
        result = user_repo.delete_by_id(99999)
        assert result is False

    def test_count_zero(self, user_repo):
        """Test count with no records."""
        count = user_repo.count()
        assert count == 0

    def test_count_multiple(self, user_repo):
        """Test count with multiple records."""
        user1 = User(username='user1', email='user1@example.com', password='pass1')
        user2 = User(username='user2', email='user2@example.com', password='pass2')
        user3 = User(username='user3', email='user3@example.com', password='pass3')
        user_repo.create(user1)
        user_repo.create(user2)
        user_repo.create(user3)

        count = user_repo.count()
        assert count == 3

    def test_count_with_filter(self, user_repo):
        """Test count with filter criteria."""
        user1 = User(username='user1', email='user1@example.com', password='pass1', is_admin=True)
        user2 = User(username='user2', email='user2@example.com', password='pass2', is_admin=False)
        user3 = User(username='user3', email='user3@example.com', password='pass3', is_admin=True)
        user_repo.create(user1)
        user_repo.create(user2)
        user_repo.create(user3)

        admin_count = user_repo.count(is_admin=True)
        assert admin_count == 2

        non_admin_count = user_repo.count(is_admin=False)
        assert non_admin_count == 1

    def test_filter_by_single_condition(self, user_repo):
        """Test filter_by with single condition."""
        user1 = User(username='alice', email='alice@example.com', password='pass1')
        user2 = User(username='bob', email='bob@example.com', password='pass2')
        user3 = User(username='charlie', email='charlie@example.com', password='pass3')
        user_repo.create(user1)
        user_repo.create(user2)
        user_repo.create(user3)

        results = user_repo.filter_by(username='alice')
        assert len(results) == 1
        assert results[0].username == 'alice'

    def test_filter_by_multiple_conditions(self, user_repo):
        """Test filter_by with multiple conditions."""
        user1 = User(username='alice', email='alice@example.com', password='pass1', is_admin=True)
        user2 = User(username='bob', email='bob@example.com', password='pass2', is_admin=False)
        user3 = User(username='charlie', email='charlie@example.com', password='pass3', is_admin=True)
        user_repo.create(user1)
        user_repo.create(user2)
        user_repo.create(user3)

        results = user_repo.filter_by(is_admin=True)
        assert len(results) == 2
        usernames = [u.username for u in results]
        assert 'alice' in usernames
        assert 'charlie' in usernames
        for user in results:
            assert user.is_admin is True

    def test_filter_by_no_results(self, user_repo):
        """Test filter_by with no matching results."""
        user = User(username='testuser', email='test@example.com', password='password123')
        user_repo.create(user)

        results = user_repo.filter_by(username='nonexistent')
        assert results == []

    def test_find_one_found(self, user_repo):
        """Test find_one when record exists."""
        user = User(username='testuser', email='test@example.com', password='password123')
        user_repo.create(user)

        result = user_repo.find_one(username='testuser')
        assert result is not None
        assert result.username == 'testuser'
        assert result.email == 'test@example.com'

    def test_find_one_not_found(self, user_repo):
        """Test find_one when record doesn't exist."""
        result = user_repo.find_one(username='nonexistent')
        assert result is None

    def test_find_one_returns_first_when_multiple(self, user_repo):
        """Test find_one returns first match when multiple exist with same attribute."""
        user1 = User(username='alice', email='alice1@example.com', password='pass1', is_admin=True)
        user2 = User(username='bob', email='bob@example.com', password='pass2', is_admin=True)
        user_repo.create(user1)
        user_repo.create(user2)

        result = user_repo.find_one(is_admin=True)
        assert result is not None
        assert result.is_admin is True
        # Should return one of the admin users
        assert result.username in ['alice', 'bob']

    def test_exists_true(self, user_repo):
        """Test exists returns True when record exists."""
        user = User(username='testuser', email='test@example.com', password='password123')
        user_repo.create(user)

        exists = user_repo.exists(username='testuser')
        assert exists is True

    def test_exists_false(self, user_repo):
        """Test exists returns False when record doesn't exist."""
        exists = user_repo.exists(username='nonexistent')
        assert exists is False

    def test_exists_with_multiple_conditions(self, user_repo):
        """Test exists with multiple conditions."""
        user = User(username='testuser', email='test@example.com', password='password123', is_admin=True)
        user_repo.create(user)

        exists = user_repo.exists(username='testuser', is_admin=True)
        assert exists is True

        exists_false = user_repo.exists(username='testuser', is_admin=False)
        assert exists_false is False

    def test_paginate_first_page(self, user_repo):
        """Test pagination on first page."""
        # Create 25 users
        users = [
            User(username=f'user{i}', email=f'user{i}@example.com', password=f'pass{i}')
            for i in range(1, 26)
        ]
        user_repo.create_many(users)

        result = user_repo.paginate(page=1, per_page=10)

        assert len(result['items']) == 10
        assert result['total'] == 25
        assert result['page'] == 1
        assert result['per_page'] == 10
        assert result['pages'] == 3

    def test_paginate_middle_page(self, user_repo):
        """Test pagination on middle page."""
        # Create 25 users
        users = [
            User(username=f'user{i}', email=f'user{i}@example.com', password=f'pass{i}')
            for i in range(1, 26)
        ]
        user_repo.create_many(users)

        result = user_repo.paginate(page=2, per_page=10)

        assert len(result['items']) == 10
        assert result['total'] == 25
        assert result['page'] == 2
        assert result['per_page'] == 10
        assert result['pages'] == 3

    def test_paginate_last_page(self, user_repo):
        """Test pagination on last page with partial results."""
        # Create 25 users
        users = [
            User(username=f'user{i}', email=f'user{i}@example.com', password=f'pass{i}')
            for i in range(1, 26)
        ]
        user_repo.create_many(users)

        result = user_repo.paginate(page=3, per_page=10)

        assert len(result['items']) == 5  # Only 5 left on last page
        assert result['total'] == 25
        assert result['page'] == 3
        assert result['per_page'] == 10
        assert result['pages'] == 3

    def test_paginate_with_filter(self, user_repo):
        """Test pagination with filter criteria."""
        # Create mix of admin and non-admin users
        users = [
            User(username=f'user{i}', email=f'user{i}@example.com', password=f'pass{i}',
                 is_admin=(i % 2 == 0))
            for i in range(1, 21)
        ]
        user_repo.create_many(users)

        result = user_repo.paginate(page=1, per_page=5, is_admin=True)

        assert len(result['items']) == 5
        assert result['total'] == 10  # Half are admins
        assert result['pages'] == 2
        assert all(user.is_admin for user in result['items'])

    def test_paginate_empty_result(self, user_repo):
        """Test pagination with no results."""
        result = user_repo.paginate(page=1, per_page=10)

        assert len(result['items']) == 0
        assert result['total'] == 0
        assert result['page'] == 1
        assert result['per_page'] == 10
        assert result['pages'] == 0
