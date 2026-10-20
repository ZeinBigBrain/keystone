-- The practice database used by most of the SQL track.
-- A small construction company: its sites, the materials it buys, the
-- suppliers it buys from, every delivery, and its staff.

CREATE TABLE sites (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT
);

CREATE TABLE materials (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    unit TEXT,
    unit_price REAL
);

CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT,
    rating INTEGER
);

CREATE TABLE deliveries (
    id INTEGER PRIMARY KEY,
    delivery_date TEXT NOT NULL,
    site TEXT REFERENCES sites(code),
    material_id INTEGER REFERENCES materials(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    quantity REAL
);

CREATE TABLE staff (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT,
    site TEXT REFERENCES sites(code),
    years INTEGER,
    manager_id INTEGER REFERENCES staff(id)
);

INSERT INTO sites VALUES
    ('RYD-N', 'North Plaza', 'Riyadh'),
    ('RYD-S', 'South Pavilion', 'Riyadh'),
    ('JED-1', 'Harbour Hall', 'Jeddah');

INSERT INTO materials VALUES
    (1, 'cement', 'binder', 'bag', 18.5),
    (2, 'sand', 'aggregate', 't', 45.0),
    (3, 'gravel', 'aggregate', 't', 52.0),
    (4, 'rebar', 'steel', 't', 2950.0),
    (5, 'bricks', 'masonry', 'pallet', 640.0),
    (6, 'timber', 'formwork', 'm3', 1150.0),
    (7, 'tiles', 'finishes', 'm2', 38.0),
    (8, 'paint', 'finishes', 'l', 22.5),
    (9, 'glass', 'finishes', 'm2', NULL);

INSERT INTO suppliers VALUES
    (1, 'Al Noor Building Supplies', 'Riyadh', 4),
    (2, 'Gulf Steel Trading', 'Dammam', 5),
    (3, 'Desert Aggregates', 'Riyadh', 3),
    (4, 'Red Sea Materials', 'Jeddah', NULL),
    (5, 'Najd Timber', 'Riyadh', 4),
    (6, 'Coastal Glass Co', 'Jeddah', NULL);

INSERT INTO deliveries VALUES
    (1, '2026-10-01', 'RYD-N', 1, 1, 40),
    (2, '2026-10-01', 'RYD-N', 2, 3, 12),
    (3, '2026-10-02', 'RYD-S', 1, 1, 25),
    (4, '2026-10-02', 'RYD-N', 4, 2, 3.5),
    (5, '2026-10-03', 'JED-1', 1, 4, 30),
    (6, '2026-10-03', 'RYD-N', 3, 3, 18),
    (7, '2026-10-04', 'RYD-S', 5, 1, 6),
    (8, '2026-10-05', 'RYD-S', 2, 3, 20),
    (9, '2026-10-05', 'JED-1', 4, 2, 2),
    (10, '2026-10-06', 'RYD-N', 6, 5, 4),
    (11, '2026-10-07', 'RYD-N', 1, 1, 35),
    (12, '2026-10-07', 'JED-1', 2, 4, 15),
    (13, '2026-10-08', 'RYD-S', 4, 2, 5),
    (14, '2026-10-09', 'RYD-N', 7, 1, 120),
    (15, '2026-10-10', 'JED-1', 5, 4, 8),
    (16, '2026-10-11', 'RYD-S', 6, 5, 3),
    (17, '2026-10-12', 'RYD-N', 2, 3, 10),
    (18, '2026-10-13', 'JED-1', 1, 4, 20),
    (19, '2026-10-14', 'RYD-S', 8, 1, 60),
    (20, '2026-10-15', 'RYD-N', 4, 2, 4),
    (21, '2026-10-16', 'JED-1', 7, 4, 90),
    (22, '2026-10-17', 'RYD-S', 1, 1, 45),
    (23, '2026-10-18', 'RYD-N', 3, 3, 22),
    (24, '2026-10-19', 'JED-1', 6, 5, 2.5);

INSERT INTO staff VALUES
    (1, 'Hana', 'project manager', 'RYD-N', 14, NULL),
    (2, 'Karim', 'site engineer', 'RYD-N', 4, 1),
    (3, 'Dina', 'quantity surveyor', 'RYD-N', 9, 1),
    (4, 'Omar', 'site engineer', 'RYD-S', 2, 6),
    (5, 'Lina', 'planner', 'RYD-S', 6, 6),
    (6, 'Sami', 'project manager', 'RYD-S', 11, NULL),
    (7, 'Rana', 'site engineer', 'JED-1', 7, 8),
    (8, 'Yousef', 'project manager', 'JED-1', 16, NULL),
    (9, 'Adel', 'foreman', 'RYD-N', 20, 2),
    (10, 'Mona', 'surveyor', 'JED-1', 3, 7);
