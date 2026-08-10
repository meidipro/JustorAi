-- SQL Migration script to create Supreme Court Judgment Staging Table in Supabase
-- Table: sc_judgment_staging

CREATE TABLE IF NOT EXISTS sc_judgment_staging (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    manifest_id text NOT NULL,
    document_type text NOT NULL DEFAULT 'SC_JUDGMENT_HCD',
    case_id text,
    division text,
    case_number text,
    case_year text,
    parties_raw text,
    judgment_date text,
    uploaded_date text,
    judges text[],
    acts_cited text[],
    sections_cited text[],
    content text NOT NULL,
    page_number integer,
    official_pdf_url text,
    source_url text,
    review_status text DEFAULT 'UNREVIEWED',
    embedding vector(1024),
    embedding_model text DEFAULT 'baai/bge-m3',
    embedding_dimension integer DEFAULT 1024,
    promoted_to_production boolean DEFAULT false,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sc_staging_manifest ON sc_judgment_staging(manifest_id);
CREATE INDEX IF NOT EXISTS idx_sc_staging_review ON sc_judgment_staging(review_status);

-- RLS Policy for full access via service role
ALTER TABLE sc_judgment_staging ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON sc_judgment_staging FOR ALL USING (true);
