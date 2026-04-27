-- Extensions for analytics database

-- Events table with partitioning by app_id and time
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY,
    app_id UUID NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    user_id VARCHAR(64),
    session_id VARCHAR(64),
    properties JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY LIST (app_id);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_events_app_time ON events (app_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_app_type_time ON events (app_id, event_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_user ON events (user_id);
CREATE INDEX IF NOT EXISTS idx_events_session ON events (session_id);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    app_id UUID NOT NULL,
    user_id VARCHAR(64),
    session_id VARCHAR(64) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_app_time ON sessions (app_id, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_session ON sessions (session_id);

-- Apps table
CREATE TABLE IF NOT EXISTS apps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    api_key VARCHAR(64) NOT NULL UNIQUE,
    secret_key VARCHAR(64) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_apps_api_key ON apps (api_key);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    app_id UUID REFERENCES apps(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_app ON users (app_id);