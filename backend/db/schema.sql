CREATE TABLE IF NOT EXISTS test_cases (
    case_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    video_url TEXT NOT NULL,
    cached_analysis JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Anonymized metadata logs (zero raw video, zero unredacted PII)
CREATE TABLE IF NOT EXISTS analysis_logs (
    analysis_id VARCHAR(64) PRIMARY KEY,
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN ('demo_case', 'user_upload')),
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    window_count INTEGER NOT NULL CHECK (window_count > 0),
    overall_risk_level VARCHAR(16) NOT NULL CHECK (overall_risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'UNKNOWN')),
    max_cv_score FLOAT,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
