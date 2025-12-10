DROP TABLE IF EXISTS registro;

CREATE TABLE registro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso VARCHAR(100),
    created_on TIMESTAMP,
    num_app INTEGER,
    num_repo INTEGER,
    num_bugs INTEGER,
    num_quality INTEGER,
    num_analisis INTEGER
);

