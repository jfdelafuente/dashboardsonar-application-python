DROP TABLE IF EXISTS daily;

CREATE TABLE daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aplicacion TEXT,
    repo TEXT,
    proveedor TEXT,
    created_on TIMESTAMP,
    num_bugs INTEGER,
    num_vulnerabilities INTEGER,
    num_code_smells INTEGER,
    num_quality INTEGER,
    num_analisis INTEGER
);

CREATE INDEX IF NOT EXISTS idx_created_on ON daily (created_on);

