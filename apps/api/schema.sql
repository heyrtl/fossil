CREATE TABLE IF NOT EXISTS fossils (
    id TEXT PRIMARY KEY,
    protocol_version TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    framework TEXT NOT NULL,
    model TEXT NOT NULL,
    task_domain TEXT NOT NULL,
    situation TEXT NOT NULL,
    context_snapshot TEXT,
    failure_type TEXT NOT NULL,
    failure_description TEXT NOT NULL,
    severity TEXT NOT NULL,
    was_irreversible INTEGER NOT NULL DEFAULT 0,
    resolution_type TEXT NOT NULL,
    resolution_description TEXT NOT NULL,
    verified INTEGER NOT NULL DEFAULT 0,
    time_to_resolve_minutes INTEGER,
    embedding TEXT NOT NULL,
    shared INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_task_domain ON fossils(task_domain);
CREATE INDEX IF NOT EXISTS idx_shared ON fossils(shared);
CREATE INDEX IF NOT EXISTS idx_timestamp ON fossils(timestamp);