"""
Legacy Scripts Package
======================

DEPRECATED: Legacy scripts kept for backward compatibility.

These scripts are from the older system architecture and should not
be used for new development. They are maintained temporarily for
compatibility but will be removed in future versions.

Available scripts (all deprecated):
- database.py: Legacy database operations (use infocodest.extensions.db instead)
- init_db.py: Old initialization (use scripts/setup/setup_database.py instead)
- daily.py: Legacy daily processing (use scripts/data/generate_daily.py instead)
- estadisticas.py: Legacy statistics (use scripts/data/generate_stats.py instead)
- proveedores.py: Legacy provider management
- registro.py: Legacy registry operations (use scripts/data/generate_registro.py instead)

For new development, use the modern alternatives in:
- scripts/setup/
- scripts/data/
- scripts/verification/
"""
