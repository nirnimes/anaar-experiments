-- Delhi Land Records MVP Database Schema
-- SQLite Database for Greater Kailash (I, II, III) and Chitranjan Park
-- Created: 2026-01-27

-- Main properties table
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plot_number TEXT NOT NULL,
    locality TEXT NOT NULL CHECK(locality IN ('Greater Kailash I', 'Greater Kailash II', 'Greater Kailash III', 'Chitranjan Park')),
    khasra_number TEXT,
    area_sqm REAL NOT NULL CHECK(area_sqm > 0),
    owner_name TEXT,
    registration_date DATE,
    last_transaction_date DATE,
    encumbrance_status TEXT NOT NULL CHECK(encumbrance_status IN ('Clear', 'Mortgaged', 'Disputed', 'Unknown')),
    property_type TEXT NOT NULL CHECK(property_type IN ('Residential', 'Commercial', 'Mixed-use')),
    market_value_estimate REAL CHECK(market_value_estimate >= 0),
    data_source TEXT NOT NULL CHECK(data_source IN ('Manual Entry', 'Public Listing', 'Crowdsourced', 'Manual Portal Query', 'User Contributed')),
    last_verified DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique plot per locality
    UNIQUE(plot_number, locality),

    -- Ensure transaction date is not before registration
    CHECK(last_transaction_date IS NULL OR registration_date IS NULL OR last_transaction_date >= registration_date)
);

-- Additional property details (JSON storage for flexible schema)
CREATE TABLE IF NOT EXISTS property_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    detail_key TEXT NOT NULL,
    detail_value TEXT, -- Stored as JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    UNIQUE(property_id, detail_key)
);

-- Property transaction history
CREATE TABLE IF NOT EXISTS property_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('Sale', 'Inheritance', 'Gift', 'Partition', 'Court Order', 'Other')),
    previous_owner TEXT,
    new_owner TEXT,
    transaction_value REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- User contributions tracking (for crowdsourced data)
CREATE TABLE IF NOT EXISTS user_contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    contributor_email TEXT,
    contribution_type TEXT CHECK(contribution_type IN ('New Property', 'Update', 'Correction', 'Verification')),
    contributed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_status TEXT DEFAULT 'Pending' CHECK(verification_status IN ('Pending', 'Verified', 'Rejected')),
    verified_by TEXT,
    verified_at TIMESTAMP,

    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
);

-- Data quality flags
CREATE TABLE IF NOT EXISTS data_quality_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    flag_type TEXT CHECK(flag_type IN ('Incomplete', 'Outdated', 'Disputed', 'Needs Verification', 'User Reported Error')),
    description TEXT,
    flagged_by TEXT,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT 0,
    resolved_at TIMESTAMP,

    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_properties_locality ON properties(locality);
CREATE INDEX IF NOT EXISTS idx_properties_plot_number ON properties(plot_number);
CREATE INDEX IF NOT EXISTS idx_properties_khasra_number ON properties(khasra_number);
CREATE INDEX IF NOT EXISTS idx_properties_encumbrance ON properties(encumbrance_status);
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_area ON properties(area_sqm);
CREATE INDEX IF NOT EXISTS idx_properties_last_verified ON properties(last_verified);
CREATE INDEX IF NOT EXISTS idx_properties_created_at ON properties(created_at);

CREATE INDEX IF NOT EXISTS idx_transactions_property_id ON property_transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON property_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_contributions_property_id ON user_contributions(property_id);
CREATE INDEX IF NOT EXISTS idx_contributions_status ON user_contributions(verification_status);

CREATE INDEX IF NOT EXISTS idx_quality_flags_property_id ON data_quality_flags(property_id);
CREATE INDEX IF NOT EXISTS idx_quality_flags_resolved ON data_quality_flags(resolved);

-- Full-text search virtual table for properties
CREATE VIRTUAL TABLE IF NOT EXISTS properties_fts USING fts5(
    plot_number,
    locality,
    khasra_number,
    owner_name,
    content=properties,
    content_rowid=id
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS properties_ai AFTER INSERT ON properties BEGIN
    INSERT INTO properties_fts(rowid, plot_number, locality, khasra_number, owner_name)
    VALUES (new.id, new.plot_number, new.locality, new.khasra_number, new.owner_name);
END;

CREATE TRIGGER IF NOT EXISTS properties_ad AFTER DELETE ON properties BEGIN
    DELETE FROM properties_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS properties_au AFTER UPDATE ON properties BEGIN
    UPDATE properties_fts SET
        plot_number = new.plot_number,
        locality = new.locality,
        khasra_number = new.khasra_number,
        owner_name = new.owner_name
    WHERE rowid = new.id;
END;

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS properties_update_timestamp
AFTER UPDATE ON properties
FOR EACH ROW
BEGIN
    UPDATE properties SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Views for common queries

-- View: Active properties (verified in last 6 months)
CREATE VIEW IF NOT EXISTS active_properties AS
SELECT * FROM properties
WHERE last_verified >= date('now', '-6 months');

-- View: Properties needing verification
CREATE VIEW IF NOT EXISTS properties_needing_verification AS
SELECT * FROM properties
WHERE last_verified < date('now', '-3 months')
OR last_verified IS NULL;

-- View: Clear title properties
CREATE VIEW IF NOT EXISTS clear_title_properties AS
SELECT * FROM properties
WHERE encumbrance_status = 'Clear';

-- View: Recent transactions (last 6 months)
CREATE VIEW IF NOT EXISTS recent_transactions AS
SELECT p.*, pt.transaction_date, pt.transaction_type, pt.transaction_value
FROM properties p
JOIN property_transactions pt ON p.id = pt.property_id
WHERE pt.transaction_date >= date('now', '-6 months')
ORDER BY pt.transaction_date DESC;

-- View: Locality statistics
CREATE VIEW IF NOT EXISTS locality_stats AS
SELECT
    locality,
    COUNT(*) as total_properties,
    AVG(area_sqm) as avg_area_sqm,
    AVG(CASE WHEN market_value_estimate > 0 THEN market_value_estimate / area_sqm END) as avg_price_per_sqm,
    SUM(CASE WHEN encumbrance_status = 'Clear' THEN 1 ELSE 0 END) as clear_count,
    SUM(CASE WHEN encumbrance_status = 'Mortgaged' THEN 1 ELSE 0 END) as mortgaged_count,
    SUM(CASE WHEN encumbrance_status = 'Disputed' THEN 1 ELSE 0 END) as disputed_count,
    SUM(CASE WHEN encumbrance_status = 'Unknown' THEN 1 ELSE 0 END) as unknown_count,
    SUM(CASE WHEN property_type = 'Residential' THEN 1 ELSE 0 END) as residential_count,
    SUM(CASE WHEN property_type = 'Commercial' THEN 1 ELSE 0 END) as commercial_count,
    MAX(last_verified) as last_updated
FROM properties
GROUP BY locality;

-- Comments for documentation
-- PRAGMA statements for optimization
PRAGMA journal_mode = WAL;  -- Write-Ahead Logging for better concurrency
PRAGMA synchronous = NORMAL; -- Balance between safety and performance
PRAGMA foreign_keys = ON;    -- Enable foreign key constraints
PRAGMA temp_store = MEMORY;  -- Store temp tables in memory for speed

-- Initial data quality check queries
-- SELECT COUNT(*) FROM properties WHERE owner_name IS NULL;
-- SELECT COUNT(*) FROM properties WHERE last_verified < date('now', '-6 months');
-- SELECT locality, COUNT(*) FROM properties GROUP BY locality;
