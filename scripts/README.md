# Scripts Directory

This directory contains utility scripts for managing the Dashboard Sonar application.

## Database Setup Script

### setup_database.py

Automated script to initialize the database and create an admin user.

#### Features

- ✅ Creates all database tables automatically
- ✅ Creates admin user with customizable credentials
- ✅ Supports all configuration environments (Development, Production, Testing)
- ✅ Interactive and non-interactive modes
- ✅ Validates existing users to prevent duplicates
- ✅ Clear error messages and progress feedback

#### Usage

**Interactive Mode (Recommended for first-time setup):**

```bash
# Development environment (default)
python scripts/setup_database.py

# Production environment
python scripts/setup_database.py --config Production

# Testing environment
python scripts/setup_database.py --config Testing
```

The script will prompt you for:
- Username (default: admin)
- Email (default: admin@example.com)
- Password (default: admin123)
- Confirmation before proceeding

**Non-Interactive Mode (for automation/CI/CD):**

```bash
# With default credentials
python scripts/setup_database.py --config Development --non-interactive

# With custom credentials
python scripts/setup_database.py \
  --config Production \
  --non-interactive \
  --username myadmin \
  --email admin@company.com \
  --password secure_password_here
```

#### Command-Line Options

- `--config CONFIG`: Configuration environment (Development, Production, Testing)
- `--non-interactive`: Run without user prompts
- `--username USERNAME`: Admin username (default: admin)
- `--email EMAIL`: Admin email (default: admin@example.com)
- `--password PASSWORD`: Admin password (default: admin123)

#### Helper Scripts

**Windows: `setup_database.bat`**

Wrapper script for Windows users:

```bash
# Run from project root
setup_database.bat

# Specify environment
setup_database.bat Production
```

**Linux/macOS: `setup_database.sh`**

Wrapper script for Linux/macOS users:

```bash
# Make executable (first time only)
chmod +x setup_database.sh

# Run from project root
./setup_database.sh

# Specify environment
./setup_database.sh Production
```

#### Examples

**Example 1: First-time setup in development**

```bash
$ python scripts/setup_database.py

============================================================
Database Setup
============================================================
Configuration: Development
Database: sqlite:///db.sqlite3
============================================================

============================================================
Admin User Configuration
============================================================
Press Enter to use default values shown in [brackets]

Username [admin]:
Email [admin@example.com]:
Password [admin123]:
Confirm password:

About to:
  1. Create/update database tables
  2. Create admin user: admin (admin@example.com)

Continue? [y/N]: y

Starting database setup...

Creating database tables...
✓ Database tables created successfully
Creating admin user 'admin'...
✓ Admin user created successfully
  Username: admin
  Email: admin@example.com
  Password: admin123

⚠️  IMPORTANT: Change the default password after first login!

============================================================
✓ Database setup completed successfully!
============================================================

You can now login with:
  Username: admin
  Password: admin123

⚠️  Remember to change your password after first login!
============================================================
```

**Example 2: Production setup with custom credentials**

```bash
$ python scripts/setup_database.py --config Production

============================================================
Admin User Configuration
============================================================
Username [admin]: prodadmin
Email [admin@example.com]: admin@mycompany.com
Password [admin123]: MySecureP@ssw0rd!
Confirm password: MySecureP@ssw0rd!

Continue? [y/N]: y

✓ Database setup completed successfully!
```

**Example 3: Automated setup for CI/CD**

```bash
python scripts/setup_database.py \
  --config Production \
  --non-interactive \
  --username cicd_admin \
  --email devops@company.com \
  --password $ADMIN_PASSWORD
```

#### Troubleshooting

**Error: "Virtual environment not activated"**

Make sure to activate your virtual environment first:

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**Error: "Admin user already exists"**

The script detects existing admin users and will not create duplicates. This is not an error - your database is already set up.

**Error: "No module named 'infocodest'"**

Make sure you're running the script from the project root directory:

```bash
cd /path/to/dashboardsonar-application-python
python scripts/setup_database.py
```

**Error: "SQLALCHEMY_DATABASE_URI not configured"**

For Production environment, make sure your `.env` file has the database configuration:

```bash
DB_ENGINE=postgresql
DB_USERNAME=your_user
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar
```

#### Security Notes

⚠️ **IMPORTANT SECURITY CONSIDERATIONS:**

1. **Change Default Password**: Always change the default password (`admin123`) immediately after first login
2. **Use Strong Passwords**: In production, use strong, randomly generated passwords
3. **Don't Commit Credentials**: Never commit passwords or `.env` files to version control
4. **Environment Variables**: For automated deployments, use environment variables instead of hardcoded passwords
5. **HTTPS Only**: Always use HTTPS in production to protect credentials in transit

#### What the Script Does

1. **Loads Configuration**: Selects the appropriate config (Development/Production/Testing)
2. **Creates Tables**: Uses SQLAlchemy to create all database tables defined in models
3. **Checks Existing Users**: Verifies if admin user already exists to prevent duplicates
4. **Hashes Password**: Uses secure PBKDF2-HMAC-SHA512 hashing for password storage
5. **Creates Admin User**: Inserts the admin user into the database
6. **Validates**: Ensures all operations completed successfully

## Other Scripts

### Legacy Scripts

The following scripts are from the legacy system and may require updates:

- `database.py` - Legacy database operations (deprecated)
- `estadisticas.py` - Statistics generation
- `proveedores.py` - Provider management
- `registro.py` - Registration operations
- `daily.py` - Daily metrics processing
- `init_db.py` - Old initialization script (use `setup_database.py` instead)

### Verification Scripts

- `verify_config.py` - Verify configuration settings
- `verify_dependencies.py` - Check installed dependencies
- `verify_requirements.py` - Validate requirements.txt

---

For more information, see the main [SETUP.md](../SETUP.md) documentation.
