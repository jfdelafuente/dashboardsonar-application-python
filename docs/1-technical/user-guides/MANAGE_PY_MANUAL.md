# manage.py - User Manual

## Overview

`manage.py` is the command-line interface (CLI) tool for managing the Dashboard Sonar application. It provides Flask-based commands for user administration, database operations, and development utilities.

Built with **Flask-Click**, this tool offers interactive prompts, validation, and comprehensive error handling for administrative tasks.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Command Reference](#command-reference)
4. [Common Workflows](#common-workflows)
5. [Validation Rules](#validation-rules)
6. [Troubleshooting](#troubleshooting)
7. [Security Considerations](#security-considerations)

---

## Prerequisites

### Environment Setup

1. **Virtual Environment**: Must be activated before running commands
   ```bash
   # Linux/Mac
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

2. **Database Configuration**: Set via `.env` file or environment variables
   ```env
   SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost/dbname
   ```

3. **Flask Application**: Must be properly configured in `config.py`

### Dependencies

- Flask 2.x or higher
- Flask-SQLAlchemy
- Click (included with Flask)
- Python 3.8+

---

## Quick Start

### List Available Commands

```bash
python manage.py commands
```

This displays all available management commands with descriptions.

### Get Help for a Specific Command

```bash
python manage.py <command> --help
```

### Example: Create Your First Admin User

```bash
python manage.py create-admin
```

The tool will interactively prompt for:
- Email address
- Username (optional)
- Password (with confirmation)

---

## Command Reference

### User Management Commands

#### 1. `create-admin` - Create Admin User

Creates a new administrator user with full validation.

**Usage:**
```bash
python manage.py create-admin
python manage.py create-admin --email admin@example.com
python manage.py create-admin --email admin@example.com --username admin
```

**Options:**
- `--email EMAIL` - Email address (will be prompted if not provided)
- `--username USERNAME` - Username (will be prompted if not provided)

**Interactive Prompts:**
1. Email address (validated for format)
2. Username (optional)
3. Password (hidden input)
4. Password confirmation

**Validation:**
- Email must be valid format (e.g., `user@domain.com`)
- Email must be unique (not already in use)
- Password must meet strength requirements (see [Validation Rules](#validation-rules))

**Example Output:**
```
=== Create Admin User ===

Email: admin@test.com
Username: admin
Password: ********
Confirm password: ********

[OK] Admin user created successfully!
   Email: admin@test.com
   Username: admin
   Is Admin: Yes
```

---

#### 2. `list-users` - List All Users

Displays a table of all registered users with their details.

**Usage:**
```bash
python manage.py list-users
```

**Output Columns:**
- ID - User database ID
- Email - User email address
- Username - Username (or '-' if not set)
- Admin - Badge indicating admin status
- Created - User creation timestamp

**Example Output:**
```
=== Users List ===

Total users: 5

ID    Email                          Username             Admin    Created
------------------------------------------------------------------------------------
1     admin@test.com                 admin                [ADMIN]  2025-12-15 10:30
2     user1@test.com                 user1                -        2025-12-16 14:22
3     user2@test.com                 user2                -        2025-12-17 09:15
```

---

#### 3. `delete-user` - Delete User

Deletes a user account after confirmation.

**Usage:**
```bash
python manage.py delete-user
python manage.py delete-user --email user@example.com
```

**Options:**
- `--email EMAIL` - Email of user to delete (will be prompted if not provided)

**Interactive Flow:**
1. Prompts for email (if not provided)
2. Displays user details for confirmation
3. Asks for confirmation before deletion
4. Deletes user if confirmed

**Safety Features:**
- Shows user details before deletion
- Requires explicit confirmation
- Cannot be undone

**Example:**
```bash
$ python manage.py delete-user --email user1@test.com

=== Delete User: user1@test.com ===

User ID: 2
Email: user1@test.com
Username: user1
Admin: No

Are you sure you want to delete this user? [y/N]: y

[OK] User user1@test.com deleted successfully.
```

---

#### 4. `make-admin` - Promote User to Admin

Grants administrator privileges to an existing user.

**Usage:**
```bash
python manage.py make-admin
python manage.py make-admin --email user@example.com
```

**Options:**
- `--email EMAIL` - Email of user to promote (will be prompted if not provided)

**Validation:**
- User must exist
- User cannot already be an admin

**Example:**
```bash
$ python manage.py make-admin --email user2@test.com

=== Promote User to Admin: user2@test.com ===

[OK] User user2@test.com promoted to admin successfully.
```

---

#### 5. `reset-password` - Reset User Password

Resets a user's password with full validation.

**Usage:**
```bash
python manage.py reset-password
python manage.py reset-password --email user@example.com
```

**Options:**
- `--email EMAIL` - Email of user (will be prompted if not provided)

**Interactive Flow:**
1. Prompts for email (if not provided)
2. Prompts for new password (hidden input)
3. Prompts for password confirmation
4. Validates password strength
5. Updates password if valid

**Validation:**
- Passwords must match
- Password must meet strength requirements
- Allows retry on validation failure

**Example:**
```bash
$ python manage.py reset-password --email admin@test.com

=== Reset Password: admin@test.com ===

New password: ********
Confirm new password: ********

[OK] Password for admin@test.com reset successfully.
```

---

### Database Utility Commands

#### 6. `db-status` - Database Connection Status

Shows database connection information and system statistics.

**Usage:**
```bash
python manage.py db-status
```

**Information Displayed:**
- Database URI (masked for security)
- Connection status (OK/FAILED)
- User statistics (total, admins, regular users)
- Database engine (SQLite, PostgreSQL, MySQL)
- SQLAlchemy version

**Example Output:**
```
=== Database Status ===

Database URI: postgresql://****:****@localhost:5432/dashboardsonar
[OK] Database connection: OK

Users:
  Total: 5
  Admins: 1
  Regular: 4

Database Engine: postgresql
SQLAlchemy Version: 2.0.23
```

**Use Cases:**
- Verify database connectivity
- Check configuration after setup
- Monitor user counts
- Troubleshoot connection issues

---

#### 7. `seed-data` - Load Sample Data

Creates test users for development and testing environments.

**Usage:**
```bash
python manage.py seed-data
python manage.py seed-data --users 10
```

**Options:**
- `--users N` - Number of test users to create (default: 5)

**What It Creates:**

1. **Admin User:**
   - Email: `admin@test.com`
   - Password: `Admin123!`
   - Username: `admin`
   - Is Admin: Yes

2. **Regular Users:**
   - Emails: `user1@test.com`, `user2@test.com`, etc.
   - Password: `User123!` (same for all test users)
   - Usernames: `user1`, `user2`, etc.
   - Is Admin: No

**Safety Features:**
- Requires confirmation before creating users
- Skips users that already exist
- Displays summary of created/skipped users
- Shows warning about test credentials

**Example:**
```bash
$ python manage.py seed-data --users 3

=== Seed Sample Data ===

WARNING: This will create 3 test users. Continue? [y/N]: y

[OK] Created admin: admin@test.com (password: Admin123!)
[OK] Created user: user1@test.com
[OK] Created user: user2@test.com

=== Seed Summary ===
   Created: 3 users
   Skipped: 0 users (already exist)
   Total: 3 users processed

[SUCCESS] Seed completed successfully!
WARNING: These are TEST credentials. Do NOT use in production!
```

**IMPORTANT SECURITY WARNING:**
- This command creates users with **predictable passwords**
- **NEVER use this in production environments**
- Only for development and testing
- Delete test users before deploying

---

### Help Command

#### 8. `commands` - List Available Commands

Displays all available management commands with descriptions.

**Usage:**
```bash
python manage.py commands
```

**What It Shows:**
- Custom management commands (user management, database utilities)
- Flask built-in commands (database migrations, routes, shell)
- Usage examples

**Example Output:**
```
=== Available Management Commands ===

create-admin        Create an admin user with validation
list-users          List all users in the system
delete-user         Delete a user by email
make-admin          Promote a user to admin status
reset-password      Reset a user's password
db-status           Show database connection status
seed-data           Load sample data for development
commands            Show this help message

Flask built-in commands:
db init             Initialize migrations
db migrate          Create migration
db upgrade          Apply migrations
db downgrade        Revert migrations
routes              Show all routes
shell               Start interactive shell

Usage:
  python manage.py <command> [options]

Examples:
  python manage.py create-admin
  python manage.py list-users
  python manage.py delete-user --email user@example.com
```

---

## Common Workflows

### Initial Setup Workflow

**Scenario:** Setting up the application for the first time.

```bash
# 1. Check database connection
python manage.py db-status

# 2. Initialize database migrations (if needed)
python manage.py db init
python manage.py db migrate -m "Initial migration"
python manage.py db upgrade

# 3. Create first admin user
python manage.py create-admin

# 4. Verify user was created
python manage.py list-users
```

---

### Development Environment Setup

**Scenario:** Setting up development environment with test data.

```bash
# 1. Create admin account
python manage.py create-admin --email dev@test.com --username devadmin

# 2. Load sample test users
python manage.py seed-data --users 10

# 3. Verify users
python manage.py list-users

# 4. Check database status
python manage.py db-status
```

---

### User Administration Workflow

**Scenario:** Managing users after deployment.

```bash
# 1. List all users
python manage.py list-users

# 2. Promote user to admin
python manage.py make-admin --email user@example.com

# 3. Reset user password (if requested)
python manage.py reset-password --email user@example.com

# 4. Remove inactive user
python manage.py delete-user --email olduser@example.com
```

---

### Password Recovery Workflow

**Scenario:** User forgot password and needs reset.

```bash
# 1. Verify user exists
python manage.py list-users

# 2. Reset password
python manage.py reset-password --email user@example.com

# 3. Inform user of new credentials (via secure channel)
```

---

## Validation Rules

### Email Validation

**Format Requirements:**
- Must contain `@` symbol
- Must contain domain (e.g., `example.com`)
- Standard email format validation using regex

**Examples:**
- Valid: `user@example.com`, `admin@company.org`, `dev.team@test.co.uk`
- Invalid: `user`, `user@`, `@example.com`, `user.example.com`

---

### Password Strength Requirements

**Minimum Requirements:**
- **Length:** At least 8 characters
- **Uppercase:** At least 1 uppercase letter (A-Z)
- **Lowercase:** At least 1 lowercase letter (a-z)
- **Digits:** At least 1 number (0-9)
- **Special:** At least 1 special character (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

**Function:** `validate_password_strength()` in [manage.py:154-202](manage.py#L154-L202)

**Examples:**
- Valid: `Admin123!`, `SecurePass#45`, `MyP@ssw0rd`
- Invalid:
  - `password` (no uppercase, no digits, no special chars)
  - `PASSWORD` (no lowercase, no digits, no special chars)
  - `Pass123` (no special characters)
  - `P@ss` (too short)

**Error Messages:**
- "Password must be at least 8 characters long"
- "Password must contain at least one uppercase letter"
- "Password must contain at least one lowercase letter"
- "Password must contain at least one number"
- "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Working outside of application context"

**Error:**
```
RuntimeError: Working outside of application context.
```

**Cause:** Flask application context not properly initialized

**Solution:**
- Ensure database is configured in `.env` file
- Check `SQLALCHEMY_DATABASE_URI` is set correctly
- Verify Flask app is created properly in `config.py`

---

#### Issue 2: "Database connection: FAILED"

**Error from `db-status` command:**
```
[ERROR] Database connection: FAILED
Error: (psycopg2.OperationalError) could not connect to server
```

**Cause:** Database server not running or configuration incorrect

**Solutions:**
1. Check database server is running:
   ```bash
   # PostgreSQL
   sudo systemctl status postgresql

   # MySQL
   sudo systemctl status mysql
   ```

2. Verify connection string in `.env`:
   ```env
   # Correct format
   SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost:5432/dbname
   ```

3. Test connection manually:
   ```bash
   psql -h localhost -U user -d dbname
   ```

---

#### Issue 3: "Email already exists"

**Error when creating user:**
```
[ERROR] Email already exists. Choose a different email.
```

**Cause:** User with that email already registered

**Solutions:**
1. List all users to check:
   ```bash
   python manage.py list-users
   ```

2. Use different email address

3. Delete old user if appropriate:
   ```bash
   python manage.py delete-user --email existing@example.com
   ```

---

#### Issue 4: "Password does not meet strength requirements"

**Error:**
```
[ERROR] Password must contain at least one uppercase letter
```

**Cause:** Password doesn't meet validation rules

**Solution:**
- Review [Password Strength Requirements](#password-strength-requirements)
- Use a password that includes:
  - Uppercase letters
  - Lowercase letters
  - Numbers
  - Special characters
- Example valid password: `SecurePass123!`

---

#### Issue 5: Unicode Characters Display Issues (Windows)

**Symptom:** Seeing strange characters instead of checkmarks/symbols

**Cause:** Windows console doesn't support Unicode symbols used in output

**Impact:** Cosmetic only - functionality not affected

**Solutions:**
1. **Temporary:** Use Windows Terminal instead of CMD
   ```bash
   wt.exe
   ```

2. **Ignore:** Symbols are just for visual feedback

3. **Permanent:** Use ASCII-only mode by setting environment variable:
   ```bash
   set PYTHONIOENCODING=utf-8
   ```

---

#### Issue 6: "Permission denied" When Running Commands

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Cause:** Insufficient file system or database permissions

**Solutions:**
1. **Database file permissions** (SQLite):
   ```bash
   chmod 664 db.sqlite3
   chmod 775 instance/
   ```

2. **Run with appropriate user** (PostgreSQL/MySQL):
   - Ensure database user has proper grants
   - Check `.env` credentials

3. **Virtual environment activation:**
   ```bash
   # Ensure venv is activated
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

---

## Security Considerations

### 1. Password Handling

**Secure Practices:**
- Passwords are never displayed in plain text
- Uses `getpass.getpass()` for hidden input
- Passwords are hashed using bcrypt before storage
- Password validation enforces strong passwords

**Implementation:**
```python
# Passwords hashed with bcrypt
from infocodest.utils.security import hash_pass
user.password = hash_pass(password).decode('ascii')
```

---

### 2. Database URI Masking

**Security Feature:**
The `db-status` command masks sensitive database credentials:

```python
# Original URI
postgresql://admin:SecretPass123@localhost:5432/dashboard

# Displayed as
postgresql://****:****@localhost:5432/dashboard
```

**Implementation:** `mask_db_uri()` function in `config/utils.py`

---

### 3. Production vs Development

**CRITICAL WARNINGS:**

#### Never Use `seed-data` in Production

```bash
# DANGEROUS in production - creates predictable passwords
python manage.py seed-data
```

**Why:**
- Creates users with known passwords (`Admin123!`, `User123!`)
- Email addresses are predictable (`admin@test.com`, `user1@test.com`)
- Security vulnerability if left in production

**Safe Alternative:**
```bash
# Create real admin with strong password
python manage.py create-admin
```

---

### 4. User Deletion

**Irreversible Action:**
- User deletion is **permanent**
- No soft-delete or recovery mechanism
- Always confirm before deleting

**Best Practices:**
1. Backup database before bulk deletions
2. Verify user details before confirming deletion
3. Consider deactivation instead (requires custom implementation)

---

### 5. Admin Privileges

**Security Implications:**
- Admin users have full system access
- Only promote trusted users
- Regularly audit admin user list

**Audit Command:**
```bash
python manage.py list-users | grep ADMIN
```

---

## Flask Built-in Commands

The following commands are provided by Flask and Flask-Migrate:

### Database Migrations

```bash
# Initialize migrations (first time only)
python manage.py db init

# Create new migration
python manage.py db migrate -m "Description of changes"

# Apply migrations
python manage.py db upgrade

# Revert last migration
python manage.py db downgrade

# Show migration history
python manage.py db history

# Show current migration version
python manage.py db current
```

---

### Application Utilities

```bash
# Show all registered routes
python manage.py routes

# Start interactive Python shell with app context
python manage.py shell

# Run development server (not recommended, use run.py instead)
python manage.py run
```

---

## Environment Configuration

### Configuration Files

1. **`.env`** - Environment variables (database, secrets)
   ```env
   SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost/db
   SECRET_KEY=your-secret-key-here
   ```

2. **`config.py`** - Application configuration classes
   - `DevelopmentConfig`
   - `ProductionConfig`
   - `TestingConfig`

---

### Environment Selection

Commands use the Flask application factory pattern. Configuration is selected when creating the app:

```python
# In manage.py
from config import config_dict
config_class = config_dict.get('Development')  # or 'Production', 'Testing'
app = create_app(config_class)
```

To change environment, modify the configuration in the application initialization or use environment variables.

---

## Examples by Use Case

### Use Case 1: New Project Setup

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Check database connection
python manage.py db-status

# 3. Initialize database
python manage.py db init
python manage.py db migrate -m "Initial schema"
python manage.py db upgrade

# 4. Create admin user
python manage.py create-admin

# 5. Verify setup
python manage.py list-users
```

---

### Use Case 2: Adding Users

```bash
# Create first admin
python manage.py create-admin --email admin@company.com --username admin

# Create regular user (requires separate user registration flow)
# OR promote existing user
python manage.py make-admin --email manager@company.com
```

---

### Use Case 3: User Support

```bash
# User forgot password
python manage.py reset-password --email user@company.com

# User requests account deletion
python manage.py delete-user --email user@company.com

# Check if user exists
python manage.py list-users | grep user@company.com
```

---

### Use Case 4: Testing/Development

```bash
# Create test environment
python manage.py seed-data --users 20

# List all test users
python manage.py list-users

# Clean up test users when done
for i in {1..19}; do
    python manage.py delete-user --email "user$i@test.com"
done
```

---

## Additional Resources

### Related Documentation

- **Database Schema**: [DATABASE_SCHEMA.md](../architecture/DATABASE_SCHEMA.md)
- **Configuration Guide**: See `config.py` for configuration options
- **User Model**: [infocodest/models/users.py](../../../infocodest/models/users.py)

### Source Code Reference

- **Main CLI File**: [manage.py](../../../manage.py)
- **Security Utilities**: [infocodest/utils/security.py](../../../infocodest/utils/security.py)
- **Database Configuration**: [config/utils.py](../../../config/utils.py)

---

## Summary

`manage.py` is your primary tool for:

- **User Management**: Create, list, promote, delete users
- **Database Operations**: Check status, run migrations
- **Development**: Seed test data, interactive shell
- **Security**: Password resets, admin privileges

**Key Points:**
- All commands include validation and confirmation
- Passwords are securely hashed
- Test data commands should NEVER be used in production
- Interactive prompts guide you through complex operations

For additional help with any command:
```bash
python manage.py <command> --help
```

---

**Last Updated**: 2025-12-19
**Version**: 1.11.0
**Author**: Dashboard Sonar Team
