# Scripts Directory

This directory contains utility scripts for managing the Dashboard Sonar application, organized by function.

## 📁 Directory Structure

```text
scripts/
├── setup/              # Initial configuration scripts (run once)
├── verification/       # Environment validation scripts
├── data/               # Data processing scripts (regular use)
├── legacy/             # Deprecated scripts (backward compatibility)
├── etl/                # ETL operations
├── sql/                # SQL schemas and queries
└── utils/              # Shared utilities
```

## 🚀 Setup Scripts (`scripts/setup/`)

Scripts for initial project configuration. Run these once during setup.

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
python scripts/setup/setup_database.py

# Production environment
python scripts/setup/setup_database.py --config Production

# Testing environment
python scripts/setup/setup_database.py --config Testing
```

The script will prompt you for:
- Username (default: admin)
- Email (default: admin@example.com)
- Password (default: admin123)
- Confirmation before proceeding

**Non-Interactive Mode (for automation/CI/CD):**

```bash
# With default credentials
python scripts/setup/setup_database.py --config Development --non-interactive

# With custom credentials
python scripts/setup/setup_database.py \
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

### init_git_workflow.sh

Configures Git workflow, hooks, and branch protection rules.

```bash
bash scripts/setup/init_git_workflow.sh
```

## ✅ Verification Scripts (`scripts/verification/`)

Scripts for validating your environment configuration.

### verify_config.py

Verifies that all configuration settings are correct.

```bash
python scripts/verification/verify_config.py
```

### verify_dependencies.py

Checks that all required dependencies are installed.

```bash
python scripts/verification/verify_dependencies.py
```

### verify_requirements.py

Validates requirements.txt for consistency and security.

```bash
python scripts/verification/verify_requirements.py
```

## 📊 Data Scripts (`scripts/data/`)

Scripts for data loading and processing. These can be run on-demand or scheduled.

### load_data.py

Loads initial data from CSV files into the database.

```bash
# Load all data from default directory (./datos)
python scripts/data/load_data.py

# Load from specific directory
python scripts/data/load_data.py --data-dir /path/to/csv/files

# Production environment
python scripts/data/load_data.py --config Production
```

### generate_daily.py

Generates daily snapshots of aggregated metrics per repository.

```bash
# Generate for today
python scripts/data/generate_daily.py

# Generate for specific date
python scripts/data/generate_daily.py --date 2024-01-15

# Clear existing data for date before generating
python scripts/data/generate_daily.py --date 2024-01-15 --clear-date

# Production environment
python scripts/data/generate_daily.py --config Production
```

### generate_registro.py

Creates audit/process registry records with global statistics.

```bash
# Generate registry for today
python scripts/data/generate_registro.py

# Custom process name
python scripts/data/generate_registro.py --process-name "Monthly Report"
```

### generate_stats.py

Generates aggregated statistics from metricas table.

```bash
# Generate statistics
python scripts/data/generate_stats.py

# Clear existing stats before regenerating
python scripts/data/generate_stats.py --clear

# Production environment
python scripts/data/generate_stats.py --config Production
```

## 🔄 ETL Scripts (`scripts/etl/`)

Extract, Transform, Load operations.

### etl.py

ETL operations and data transformations.

```bash
python scripts/etl/etl.py
```

## 🗃️ SQL Files (`scripts/sql/`)

SQL schemas and queries used by scripts.

- `schema.sql` - Main database schema
- `daily.sql` - Daily metrics table schema
- `stats.sql` - Statistics table schema
- `registro.sql` - Registry table schema
- `proveedores.sql` - Providers table schema

## 🛠️ Utilities (`scripts/utils/`)

Shared utility functions used across scripts.

### utils.py

Common utility functions for CSV processing, data extraction, etc.

```python
from scripts.utils.utils import extract_from_csv, load_to_csv
```

## 📦 Legacy Scripts (`scripts/legacy/`)

⚠️ **DEPRECATED**: These scripts are from the older system architecture.

**Do not use for new development.** They are maintained temporarily for backward compatibility.

- `database.py` - Legacy database operations ❌ Use `infocodest.extensions.db` instead
- `init_db.py` - Old initialization ❌ Use `scripts/setup/setup_database.py` instead
- `daily.py` - Legacy daily processing ❌ Use `scripts/data/generate_daily.py` instead
- `estadisticas.py` - Legacy statistics ❌ Use `scripts/data/generate_stats.py` instead
- `proveedores.py` - Legacy provider management
- `registro.py` - Legacy registry ❌ Use `scripts/data/generate_registro.py` instead

## 🔍 Examples

### First-time setup in development

```bash
$ python scripts/setup/setup_database.py

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

### Production setup with custom credentials

```bash
$ python scripts/setup/setup_database.py --config Production

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

### Automated setup for CI/CD

```bash
python scripts/setup/setup_database.py \
  --config Production \
  --non-interactive \
  --username cicd_admin \
  --email devops@company.com \
  --password $ADMIN_PASSWORD
```

## 🔍 Troubleshooting

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
python scripts/setup/setup_database.py
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

## 🔐 Security Notes

⚠️ **IMPORTANT SECURITY CONSIDERATIONS:**

1. **Change Default Password**: Always change the default password (`admin123`) immediately after first login
2. **Use Strong Passwords**: In production, use strong, randomly generated passwords
3. **Don't Commit Credentials**: Never commit passwords or `.env` files to version control
4. **Environment Variables**: For automated deployments, use environment variables instead of hardcoded passwords
5. **HTTPS Only**: Always use HTTPS in production to protect credentials in transit

## 📚 Additional Documentation

For more information, see:

- [SETUP.md](../SETUP.md) - Main setup documentation
- [config/README.md](../config/README.md) - Configuration system
- [docs/MEJORAS_CONFIGURACION.md](../docs/MEJORAS_CONFIGURACION.md) - Configuration improvements
