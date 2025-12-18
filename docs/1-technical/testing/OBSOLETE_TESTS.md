# Obsolete Tests - Require Team Review

**Date**: Diciembre 2025
**Status**: Tests fail because routes don't exist

---

## Tests Identified as Obsolete

These tests are failing because the routes they test do not exist in the codebase. They were likely created for features that were removed or renamed.

### 1. test_get_repos
**File**: `tests/funcional/test_api.py:41`
**Route Tested**: `/api/charts_data`
**Status**: Route does not exist (404)

**Evidence**:
```bash
$ grep -r "@.*route.*charts_data" infocodest/**/*.py
# Result: No matches found
```

**Recommendation**:
- Option A: Delete this obsolete test
- Option B: Update to correct route if feature was renamed
- Option C: Implement `/api/charts_data` endpoint if feature is needed

---

### 2. test_historico_metricas_page
**File**: `tests/funcional/test_home.py:58`
**Route Tested**: `/metricas/historico`
**Status**: Route does not exist (404)

**Evidence**:
```bash
$ grep -r "@.*route.*/metricas/historico" infocodest/**/*.py
# Result: No matches found
```

**Similar existing routes**:
- `/metricas` - Main metrics page
- `/metricas/proveedores` - Provider metrics
- `/charts_historico` - Historical charts (different blueprint)

**Recommendation**:
- Option A: Delete this obsolete test
- Option B: Update to `/charts_historico` if that's the intended route
- Option C: Implement `/metricas/historico` route if feature is needed

---

## Action Required

**Team Decision Needed**:
1. Were these features intentionally removed?
2. Were the routes renamed and tests not updated?
3. Should these features be re-implemented?

**Until Decision Made**:
- Tests remain in codebase but are known to fail
- Pass rate: 277/279 (99.3%)
- No impact on Priority 1 objectives (all completed)

---

**Note**: All originally failing tests from Priority 1 analysis have been fixed. These 2 tests are separate issues discovered during testing.
