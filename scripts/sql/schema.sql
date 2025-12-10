DROP TABLE IF EXISTS metricas;

CREATE TABLE metricas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT,
    aplicacion TEXT,
    fecha TEXT,
    bugs INTEGER,
    reliability_rating INTEGER,
    reliability_label TEXT,
    vulnerabilities INTEGER,
    security_rating INTEGER,
    security_label TEXT,
    code_smells INTEGER,
    sqale_rating INTEGER,
    sqale_label TEXT,
    alert_status TEXT,
    project TEXT,
    complexity INTEGER,
    coverage FLOAT,
    unit_tests TEXT,
    ncloc INTEGER,
    duplicated_line_density FLOAT,
    sqale_index INTEGER,
    sqale_debt_ratio FLOAT,
    size TEXT,
    dloc_label TEXT,
    coverage_label TEXT,
    quality_gate TEXT
);

CREATE INDEX IF NOT EXISTS idx_aplicacion ON metricas (aplicacion);

DROP TABLE IF EXISTS historico;

CREATE TABLE historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT,
    aplicacion TEXT,
    fecha TEXT,
    bugs INTEGER,
    reliability_rating INTEGER,
    reliability_label TEXT,
    vulnerabilities INTEGER,
    security_rating INTEGER,
    security_label TEXT,
    code_smells INTEGER,
    sqale_rating INTEGER,
    sqale_label TEXT,
    alert_status TEXT,
    project TEXT,
    complexity INTEGER,
    coverage FLOAT,
    unit_tests TEXT,
    ncloc FLOAT,
    duplicated_line_density INTEGER,
    sqale_index INTEGER,
    sqale_debt_ratio FLOAT,
    size TEXT,
    dloc_label TEXT,
    coverage_label TEXT,
    quality_gate TEXT
);



DROP TABLE IF EXISTS proveedor;

CREATE TABLE proveedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aplicacion TEXT,
    proveedor TEXT,
    tipo TEXT
);