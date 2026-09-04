CREATE TABLE IF NOT EXISTS upload_jobs (
    id UUID PRIMARY KEY,
    status TEXT NOT NULL,
    title TEXT,
    user_id TEXT,
    chunks_done INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    document_id UUID,
    error TEXT,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_upload_jobs_user ON upload_jobs(user_id);
