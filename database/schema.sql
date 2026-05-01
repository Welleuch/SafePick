-- PESE Database Schema for Cloudflare D1 (SQLite)
-- Compatible with Cloudflare D1, switchable to Supabase/PostgreSQL later

-- Robots Table
CREATE TABLE IF NOT EXISTS robots (
    id TEXT PRIMARY KEY,
    brand TEXT NOT NULL,
    model_name TEXT NOT NULL,
    robot_type TEXT NOT NULL,
    max_payload_kg REAL NOT NULL,
    max_inertia_kgm2 REAL NOT NULL,
    flange_iso_code TEXT NOT NULL,
    max_v_ms REAL NOT NULL,
    max_a_ms2 REAL NOT NULL,
    io_max_current_a REAL NOT NULL,
    protocols TEXT NOT NULL,
    extra_specs TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Grippers Table
CREATE TABLE IF NOT EXISTS grippers (
    id TEXT PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    model_name TEXT NOT NULL,
    mass_kg REAL NOT NULL,
    inertia_cm REAL NOT NULL,
    com_offset_z_mm REAL NOT NULL,
    grip_offset_z_mm REAL NOT NULL,
    mounting_pattern TEXT NOT NULL,
    peak_current_a REAL NOT NULL,
    protocols TEXT NOT NULL,
    extra_specs TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Validations Table (The Technical Audit)
CREATE TABLE IF NOT EXISTS validations (
    id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    junior_engineer_id TEXT,
    robot_id TEXT NOT NULL,
    gripper_id TEXT NOT NULL,
    workpiece_mass_kg REAL NOT NULL,
    target_distance_m REAL NOT NULL,
    calculated_inertia REAL,
    calculated_util REAL,
    status TEXT DEFAULT 'DRAFT',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (robot_id) REFERENCES robots(id),
    FOREIGN KEY (gripper_id) REFERENCES grippers(id)
);

-- Critical Assumptions Table
CREATE TABLE IF NOT EXISTS assumptions (
    id TEXT PRIMARY KEY,
    validation_id TEXT NOT NULL,
    assumption_text TEXT NOT NULL,
    is_confirmed INTEGER DEFAULT 0,
    confirmed_at TEXT,
    FOREIGN KEY (validation_id) REFERENCES validations(id)
);

-- Knowledge Tips Table (Senior Engineer Tips)
CREATE TABLE IF NOT EXISTS knowledge_tips (
    id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT,
    severity TEXT NOT NULL,
    tip_text_de TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- License Bundles Table (Project-based pricing model)
CREATE TABLE IF NOT EXISTS license_bundles (
    id TEXT PRIMARY KEY,
    integrator_id TEXT NOT NULL,
    total_validations INTEGER NOT NULL,
    used_validations INTEGER DEFAULT 0,
    purchase_date TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT
);

-- Insert default robots (Delta robots for pharma/food)
INSERT OR IGNORE INTO robots (id, brand, model_name, robot_type, max_payload_kg, max_inertia_kgm2, flange_iso_code, max_v_ms, max_a_ms2, io_max_current_a, protocols)
VALUES
    ('kuka-kr-3-delta', 'KUKA', 'KR 3 Delta', 'Delta', 3.0, 0.05, 'ISO 9409-1-31.5-4-M5', 10.0, 50.0, 2.0, '["Profinet", "EtherCAT"]'),
    ('fanuc-m-1ia', 'Fanuc', 'M-1iA', 'Delta', 1.0, 0.02, 'ISO 9409-1-31.5-4-M5', 8.0, 40.0, 2.0, '["Profinet", "Ethernet/IP"]'),
    ('abb-irb-360', 'ABB', 'IRB 360', 'Delta', 3.0, 0.05, 'ISO 9409-1-50-4-M6', 10.0, 50.0, 2.0, '["Profinet", "DeviceNet"]');

-- Insert default grippers
INSERT OR IGNORE INTO grippers (id, manufacturer, model_name, mass_kg, inertia_cm, com_offset_z_mm, grip_offset_z_mm, mounting_pattern, peak_current_a, protocols)
VALUES
    ('schunk-pgn-plus-p-100', 'Schunk', 'PGN-plus-P 100', 0.45, 0.0001, 50, 80, 'ISO 9409-1-31.5-4-M5', 1.5, '["Profinet", "EtherCAT"]'),
    ('zimmer-gp400', 'Zimmer', 'GP400', 0.38, 0.00008, 45, 70, 'ISO 9409-1-31.5-4-M5', 1.2, '["Profinet", "EtherCAT"]'),
    ('festo-hew-16', 'Festo', 'HEW-16', 0.25, 0.00005, 40, 60, 'ISO 9409-1-31.5-4-M5', 1.0, '["Profinet", "IO-Link"]');

-- Insert default assumptions for validation
INSERT OR IGNORE INTO assumptions (id, validation_id, assumption_text, is_confirmed)
VALUES
    ('assume-1', 'temp', 'Werkstückoberfläche ist trocken, sauber und für Vakuumsauger geeignet.', 0),
    ('assume-2', 'temp', 'Schwerpunkt (CoM) des Greifers weicht nicht mehr als 5mm von der CAD-Vorgabe ab.', 0),
    ('assume-3', 'temp', 'Die Umgebungstemperatur am Einsatzort überschreitet nicht 40°C.', 0),
    ('assume-4', 'temp', 'Pick-up Zeit (Vakuumaufbau/Greifschluss) ist konstant ≤ 100ms.', 0);