-- SentinelGuard Phase II Schema Definition
-- Capture screenshots of each CREATE TABLE statement for Phase II submission.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS analysts (
    analyst_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('Tier 1', 'Tier 2', 'Tier 3', 'Manager')),
    on_call INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_analysts_email ON analysts(email);

CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT NOT NULL UNIQUE,
    ip_address TEXT NOT NULL UNIQUE,
    business_owner TEXT NOT NULL,
    criticality TEXT NOT NULL CHECK (criticality IN ('Low', 'Moderate', 'High', 'Critical')),
    last_patch_date DATE
);

CREATE TABLE IF NOT EXISTS security_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    ingest_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL,
    raw_log TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('New', 'Triaged', 'In Progress', 'Resolved')),
    CONSTRAINT fk_security_events_asset
        FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_security_events_asset_status
    ON security_events(asset_id, status);

CREATE TABLE IF NOT EXISTS ai_assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    model_version TEXT NOT NULL,
    risk_score REAL NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
    severity_label TEXT NOT NULL CHECK (severity_label IN ('Low', 'Medium', 'High', 'Critical')),
    recommended_action TEXT,
    summary TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ai_assessments_event
        FOREIGN KEY (event_id) REFERENCES security_events(event_id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_assessments_event_model
    ON ai_assessments(event_id, model_version);

CREATE TABLE IF NOT EXISTS incident_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    assigned_to INTEGER,
    task_description TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
    due_date DATE,
    status TEXT NOT NULL CHECK (status IN ('Pending', 'In Progress', 'Blocked', 'Complete')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_incident_tasks_event
        FOREIGN KEY (event_id) REFERENCES security_events(event_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_incident_tasks_assigned
        FOREIGN KEY (assigned_to) REFERENCES analysts(analyst_id)
        ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_incident_tasks_event_description
    ON incident_tasks(event_id, task_description);

CREATE TABLE IF NOT EXISTS threat_intel_matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    indicator_type TEXT NOT NULL CHECK (indicator_type IN ('IP', 'Domain', 'Hash', 'URL')),
    indicator_value TEXT NOT NULL,
    threat_actor TEXT,
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    CONSTRAINT fk_threat_matches_event
        FOREIGN KEY (event_id) REFERENCES security_events(event_id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_threat_intel_indicator
    ON threat_intel_matches(event_id, indicator_value);

CREATE TABLE IF NOT EXISTS compliance_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL UNIQUE,
    generated_by INTEGER NOT NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    regulation TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    export_path TEXT,
    CONSTRAINT fk_compliance_reports_event
        FOREIGN KEY (event_id) REFERENCES security_events(event_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_compliance_reports_author
        FOREIGN KEY (generated_by) REFERENCES analysts(analyst_id)
        ON UPDATE CASCADE
);

