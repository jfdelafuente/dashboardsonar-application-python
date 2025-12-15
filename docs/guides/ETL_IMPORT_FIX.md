# ETL Import Fix - Technical Guide

## Problem Description

The ETL scripts (`scripts/etl/etl.py` and `scripts/utils/utils.py`) had import issues when executed from different contexts:

1. **From project root**: `python scripts/data/load_data.py`
2. **As a module**: `from scripts.etl.etl import transformar_metricas`
3. **As standalone script**: Running scripts directly

### Error Messages

```python
ModuleNotFoundError: No module named 'scripts'
ImportError: attempted relative import with no known parent package
```

## Root Cause

The `scripts` directory was not a proper Python package:
- Missing `scripts/__init__.py`
- Inflexible import statements in `etl.py`
- No fallback mechanism for different execution contexts

## Solution Implemented

### 1. Convert `scripts` to a Python Package

Created `scripts/__init__.py`:

```python
"""
Scripts Package
================

This package contains utility scripts for data management, ETL operations,
database setup, and verification tasks.

Modules:
    - data: Data loading and generation scripts
    - etl: Extract, Transform, Load operations
    - setup: Database and environment setup
    - utils: Utility functions for data processing
    - verification: Configuration and dependency verification
    - legacy: Legacy scripts (deprecated, kept for reference)

Created: Post-Phase 10 - Scripts reorganization
"""

__version__ = "1.0.0"
```

### 2. Flexible Import System in `etl.py`

Updated `scripts/etl/etl.py` with multi-level fallback import mechanism:

```python
"""
ETL Module
==========

Extract, Transform, Load operations for SonarQube metrics data.

Functions:
    - transformar_metricas: Transform raw metrics data
    - transformar_historico: Transform historical analysis data
    - transformar_stats: Transform aggregated statistics

Created: Post-Phase 10 - ETL operations
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Support both absolute and relative imports
try:
    # Try relative import first (when used as a package)
    from ..utils.utils import extract_from_csv, load_to_csv
except ImportError:
    try:
        # Try absolute import (when scripts is in sys.path)
        from scripts.utils.utils import extract_from_csv, load_to_csv
    except ImportError:
        # Fallback: add scripts to path and import
        scripts_dir = Path(__file__).parent.parent.absolute()
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from utils.utils import extract_from_csv, load_to_csv
```

### 3. Enhanced Documentation

Added comprehensive docstrings to both modules:

#### `scripts/utils/utils.py`

```python
"""
Utils Module
============

Utility functions for data extraction and loading operations.

Functions:
    - extract_from_csv: Extract data from CSV files
    - extract_from_json: Extract data from JSON files
    - extract_from_excel: Extract data from Excel files
    - load_to_csv: Save DataFrame to CSV file
    - load_to_json: Save data to JSON file

Created: Post-Phase 10 - Utility functions
"""
```

All functions now have proper docstrings with Args and Returns sections.

## How It Works

### Import Resolution Order

1. **Relative Import** (Package context):
   ```python
   from ..utils.utils import extract_from_csv
   ```
   - Works when: `scripts` is imported as a package
   - Example: `from scripts.etl.etl import transformar_metricas`

2. **Absolute Import** (sys.path context):
   ```python
   from scripts.utils.utils import extract_from_csv
   ```
   - Works when: Project root is in `sys.path`
   - Example: Scripts like `load_data.py` that add project root to path

3. **Dynamic Path Import** (Fallback):
   ```python
   scripts_dir = Path(__file__).parent.parent.absolute()
   sys.path.insert(0, str(scripts_dir))
   from utils.utils import extract_from_csv
   ```
   - Works when: None of the above work
   - Adds `scripts/` directory to path dynamically

## Testing

### Test 1: As Package Import

```python
# From project root
import sys
sys.path.insert(0, '.')
from scripts.etl.etl import transformar_metricas, transformar_historico, transformar_stats
print("✅ Package import successful!")
```

### Test 2: Via load_data.py

```bash
cd "c:\My Program Files\workspace-claude\dashboardsonar-application-python"
python scripts/data/load_data.py --help
```

Should show help without import errors.

### Test 3: Direct Execution

```bash
cd scripts/etl
python -c "import etl; print(etl.transformar_metricas)"
```

## Benefits

### ✅ Compatibility

- Works in all execution contexts
- No breaking changes to existing code
- Backward compatible with old import style

### ✅ Maintainability

- Clear documentation
- Explicit import fallback logic
- Easy to debug import issues

### ✅ Best Practices

- Proper Python package structure
- Comprehensive docstrings
- PEP 8 compliant

## Files Modified

1. **scripts/__init__.py** (new)
   - Converts scripts directory to Python package
   - Provides package-level documentation

2. **scripts/etl/etl.py** (modified)
   - Flexible import system with fallbacks
   - Module-level docstring
   - No changes to function logic

3. **scripts/utils/utils.py** (modified)
   - Module-level docstring
   - Function-level docstrings with Args/Returns
   - No changes to function logic

## Usage Examples

### Example 1: From Application Code

```python
# In infocodest/services/some_service.py
from scripts.etl.etl import transformar_metricas

def process_metrics(csv_file):
    data = transformar_metricas(csv_file)
    return data
```

### Example 2: From Data Scripts

```python
# In scripts/data/load_data.py
from scripts.etl.etl import transformar_metricas, transformar_historico
from scripts.utils.utils import extract_from_csv

# Already works - no changes needed
```

### Example 3: From Tests

```python
# In tests/unit/test_etl.py
from scripts.etl.etl import transformar_stats
import pandas as pd

def test_transformar_stats():
    df = pd.DataFrame({...})
    result = transformar_stats(df)
    assert result is not None
```

## Troubleshooting

### Issue: Still getting ImportError

**Solution**: Ensure you're running from project root:

```bash
cd "c:\My Program Files\workspace-claude\dashboardsonar-application-python"
python scripts/data/load_data.py
```

### Issue: Pandas not found

**Solution**: Install requirements:

```bash
pip install -r requirements.txt
```

### Issue: Relative import in non-package

**Solution**: This is now handled automatically by the fallback mechanism.

## Future Improvements

### Optional Enhancements

1. **Type Hints**: Add full type hints to all functions
2. **Async Support**: Add async versions of extract functions
3. **Error Handling**: Enhanced error messages for import failures
4. **Testing**: Unit tests for import mechanisms

### Example Type Hints

```python
from typing import Union
from pathlib import Path
import pandas as pd

def extract_from_csv(
    file_to_process: Union[str, Path]
) -> pd.DataFrame:
    """
    Extract data from a CSV file.

    Args:
        file_to_process: Path to the CSV file (str or Path object)

    Returns:
        pandas.DataFrame: DataFrame containing the CSV data

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        pd.errors.ParserError: If the CSV is malformed
    """
    dataframe = pd.read_csv(file_to_process, sep=';')
    return dataframe
```

## Commit Information

**Commit**: 0d7696d
**Message**: `fix: resolve ETL import issues in scripts package`
**Branch**: develop
**Date**: 2024-01-15

## Related Documentation

- [Scripts README](../../scripts/README.md) - Overview of all scripts
- [Data Loading Guide](../../scripts/data/README.md) - Data loading documentation
- [Development Guide](../DEVELOPMENT_GUIDE.md) - General development practices

---

**Last Updated**: 2024-01-15
**Maintained By**: Development Team
