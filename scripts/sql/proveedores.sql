DROP TABLE IF EXISTS proveedor;

CREATE TABLE proveedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aplicacion TEXT,
    proveedor TEXT,
    tipo TEXT
);

CREATE INDEX IF NOT EXISTS idx_aplicacion ON proveedor (aplicacion);