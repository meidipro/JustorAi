BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Canonical Legal Instruments (Acts, Ordinances, Orders, Rules)
CREATE TABLE IF NOT EXISTS legal_instruments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_title TEXT NOT NULL UNIQUE,
    short_title TEXT,
    instrument_type TEXT NOT NULL CHECK (
        instrument_type IN (
            'principal_act','amendment_act','ordinance','rules',
            'regulation','order','constitution','other'
        )
    ),
    act_number TEXT,
    year INTEGER,
    jurisdiction TEXT NOT NULL DEFAULT 'Bangladesh',
    enacted_at DATE,
    published_at DATE,
    effective_from DATE,
    effective_to DATE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (
        status IN (
            'active','repealed','expired','spent',
            'superseded','partially_repealed'
        )
    ),
    repealed_by UUID REFERENCES legal_instruments(id),
    official_url TEXT,
    gazette_url TEXT,
    official_source_verified BOOLEAN NOT NULL DEFAULT FALSE,
    source_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_legal_instruments_title
ON legal_instruments(canonical_title);

CREATE INDEX IF NOT EXISTS idx_legal_instruments_status
ON legal_instruments(status);

-- 2. Legal Instrument Aliases
CREATE TABLE IF NOT EXISTS legal_instrument_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES legal_instruments(id) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    normalized_alias TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_instrument_aliases_instrument
ON legal_instrument_aliases(instrument_id);

-- 3. Canonical Legal Provisions (Sections, Subsections, Clauses)
CREATE TABLE IF NOT EXISTS legal_provisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES legal_instruments(id) ON DELETE CASCADE,
    section_number TEXT NOT NULL,
    subsection TEXT,
    paragraph TEXT,
    clause TEXT,
    heading TEXT,
    provision_type TEXT NOT NULL DEFAULT 'section',
    parent_provision_id UUID REFERENCES legal_provisions(id),
    canonical_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_legal_provision_lookup
ON legal_provisions(instrument_id, section_number, subsection, clause);

-- 4. Provision Versions (Temporal / Amendment History)
CREATE TABLE IF NOT EXISTS provision_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provision_id UUID NOT NULL REFERENCES legal_provisions(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    legal_text TEXT NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (
        status IN ('active','repealed','omitted','superseded')
    ),
    created_by_instrument_id UUID REFERENCES legal_instruments(id),
    supersedes_version_id UUID REFERENCES provision_versions(id),
    official_url TEXT,
    source_hash TEXT NOT NULL,
    official_source_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    CHECK (valid_to IS NULL OR valid_to > valid_from),
    UNIQUE(provision_id, version_number)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_current_provision_version
ON provision_versions(provision_id)
WHERE is_current = TRUE;

CREATE INDEX IF NOT EXISTS idx_provision_versions_temporal
ON provision_versions(provision_id, valid_from, valid_to);

-- 5. Amendment Events
CREATE TABLE IF NOT EXISTS amendment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amending_instrument_id UUID NOT NULL REFERENCES legal_instruments(id),
    target_provision_id UUID NOT NULL REFERENCES legal_provisions(id),
    operation TEXT NOT NULL CHECK (
        operation IN (
            'INSERT','SUBSTITUTE','OMIT','REPEAL','ADD_SUBSECTION',
            'DELETE_SUBSECTION','RENUMBER','ADD_PROVISO',
            'SUBSTITUTE_WORDS','OTHER'
        )
    ),
    effective_from DATE NOT NULL,
    old_version_id UUID REFERENCES provision_versions(id),
    new_version_id UUID REFERENCES provision_versions(id),
    old_text TEXT,
    new_text TEXT,
    official_url TEXT,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Provision Relationships (Hierarchy / Special vs General)
CREATE TABLE IF NOT EXISTS provision_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_provision_id UUID NOT NULL REFERENCES legal_provisions(id) ON DELETE CASCADE,
    target_provision_id UUID NOT NULL REFERENCES legal_provisions(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK (
        relationship_type IN (
            'CROSS_REFERENCE','SPECIAL_OVER_GENERAL','EXCEPTION_TO',
            'SUBJECT_TO','PROCEDURAL_COMPANION','SUBSTANTIVE_COMPANION',
            'DEFINITION_FOR','SUPERSEDES','AMENDS','REPEALS'
        )
    ),
    explanation TEXT,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(source_provision_id, target_provision_id, relationship_type)
);

-- 7. Derived Legal Search Chunks (FTS + Vector 1024-dim)
CREATE TABLE IF NOT EXISTS legal_search_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provision_version_id UUID REFERENCES provision_versions(id) ON DELETE CASCADE,
    instrument_id UUID NOT NULL REFERENCES legal_instruments(id),
    provision_id UUID REFERENCES legal_provisions(id),
    source_role TEXT NOT NULL CHECK (
        source_role IN (
            'CURRENT_CONSOLIDATED_LAW','HISTORICAL_LAW',
            'AMENDMENT_INSTRUMENT','CASE_LAW','RULES','GAZETTE','SECONDARY'
        )
    ),
    act_name TEXT,
    section_number TEXT,
    heading TEXT,
    search_text TEXT NOT NULL,
    embedding vector(1024),
    fts TSVECTOR GENERATED ALWAYS AS (
        to_tsvector(
            'simple',
            coalesce(act_name, '') || ' ' ||
            coalesce(section_number, '') || ' ' ||
            coalesce(heading, '') || ' ' ||
            coalesce(search_text, '')
        )
    ) STORED,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(provision_version_id, source_role)
);

CREATE INDEX IF NOT EXISTS idx_legal_search_fts
ON legal_search_chunks USING GIN(fts);

CREATE INDEX IF NOT EXISTS idx_legal_search_embedding_hnsw
ON legal_search_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_legal_search_section
ON legal_search_chunks(instrument_id, section_number);

-- 8. Legal Cases & Case-Provision Links
CREATE TABLE IF NOT EXISTS legal_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_case_id TEXT UNIQUE,
    case_title TEXT NOT NULL,
    citation TEXT,
    court_division TEXT,
    judgment_date DATE,
    year INTEGER,
    official_url TEXT,
    judgment_text TEXT,
    ratio_summary TEXT,
    ratio_type TEXT CHECK (
        ratio_type IN ('VERBATIM_EXCERPT','EDITORIAL_SUMMARY','NONE')
    ),
    human_verified BOOLEAN DEFAULT FALSE,
    source_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS case_provision_links (
    case_id UUID NOT NULL REFERENCES legal_cases(id) ON DELETE CASCADE,
    provision_id UUID NOT NULL REFERENCES legal_provisions(id),
    relationship_type TEXT NOT NULL CHECK (
        relationship_type IN (
            'INTERPRETED','APPLIED','DISTINGUISHED','MENTIONED','CHALLENGED','OTHER'
        )
    ),
    PRIMARY KEY(case_id, provision_id, relationship_type)
);

-- 9. Provision Version Candidates (Review Queue)
CREATE TABLE IF NOT EXISTS provision_version_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provision_id UUID NOT NULL REFERENCES legal_provisions(id),
    proposed_text TEXT NOT NULL,
    proposed_valid_from DATE NOT NULL,
    source_instrument_id UUID REFERENCES legal_instruments(id),
    operation TEXT,
    official_url TEXT,
    source_hash TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'PENDING' CHECK (
        review_status IN ('PENDING','APPROVED','REJECTED','PROMOTED')
    ),
    reviewer TEXT,
    review_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 10. Legal Answer Audits (Telemetry & Quality Tracking)
CREATE TABLE IF NOT EXISTS legal_answer_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_run_id UUID,
    query_text TEXT NOT NULL,
    persona TEXT,
    temporal_mode TEXT,
    as_of_date DATE,
    router_json JSONB,
    evidence_json JSONB,
    draft_json JSONB,
    validation_json JSONB,
    critic_pass BOOLEAN,
    regeneration_count INTEGER DEFAULT 0,
    abstained BOOLEAN DEFAULT FALSE,
    law_data_version TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Legacy backward compatibility bridges
ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS legal_instrument_id UUID REFERENCES legal_instruments(id);

ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS legal_provision_id UUID REFERENCES legal_provisions(id);

ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS legal_version_id UUID REFERENCES provision_versions(id);

-- 11. Hybrid Search RPC (Semantic + FTS with RRF)
CREATE OR REPLACE FUNCTION hybrid_search_law_v2(
    p_query_text TEXT,
    p_query_embedding vector(1024),
    p_query_date DATE DEFAULT CURRENT_DATE,
    p_instrument_id UUID DEFAULT NULL,
    p_match_count INTEGER DEFAULT 12
)
RETURNS TABLE (
    search_chunk_id UUID,
    instrument_id UUID,
    provision_id UUID,
    provision_version_id UUID,
    act_name TEXT,
    section_number TEXT,
    heading TEXT,
    legal_text TEXT,
    official_url TEXT,
    source_role TEXT,
    rrf_score DOUBLE PRECISION
)
LANGUAGE SQL
STABLE
AS $$
WITH eligible AS (
    SELECT
        lsc.*,
        pv.legal_text,
        pv.official_url,
        pv.valid_from,
        pv.valid_to,
        pv.status
    FROM legal_search_chunks lsc
    JOIN provision_versions pv
        ON pv.id = lsc.provision_version_id
    WHERE
        (p_instrument_id IS NULL OR lsc.instrument_id = p_instrument_id)
        AND pv.status = 'active'
        AND pv.valid_from <= p_query_date
        AND (pv.valid_to IS NULL OR p_query_date < pv.valid_to)
        AND lsc.source_role IN ('CURRENT_CONSOLIDATED_LAW','HISTORICAL_LAW')
),
semantic AS (
    SELECT
        id,
        ROW_NUMBER() OVER (ORDER BY embedding <=> p_query_embedding) AS semantic_rank
    FROM eligible
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> p_query_embedding
    LIMIT GREATEST(p_match_count * 4, 20)
),
lexical AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            ORDER BY ts_rank_cd(
                fts,
                plainto_tsquery('simple', p_query_text)
            ) DESC
        ) AS lexical_rank
    FROM eligible
    WHERE fts @@ plainto_tsquery('simple', p_query_text)
    ORDER BY ts_rank_cd(
        fts,
        plainto_tsquery('simple', p_query_text)
    ) DESC
    LIMIT GREATEST(p_match_count * 4, 20)
),
combined AS (
    SELECT
        e.id,
        COALESCE(1.0 / (60.0 + s.semantic_rank), 0)
        + COALESCE(1.0 / (60.0 + l.lexical_rank), 0) AS score
    FROM eligible e
    LEFT JOIN semantic s ON s.id = e.id
    LEFT JOIN lexical l ON l.id = e.id
    WHERE s.id IS NOT NULL OR l.id IS NOT NULL
)
SELECT
    e.id,
    e.instrument_id,
    e.provision_id,
    e.provision_version_id,
    e.act_name,
    e.section_number,
    e.heading,
    e.legal_text,
    e.official_url,
    e.source_role,
    c.score
FROM combined c
JOIN eligible e ON e.id = c.id
ORDER BY c.score DESC
LIMIT p_match_count;
$$;

-- 12. Safe Amendment Promotion RPC
CREATE OR REPLACE FUNCTION promote_provision_candidate(
    p_candidate_id UUID,
    p_reviewer TEXT
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    candidate provision_version_candidates%ROWTYPE;
    current_row provision_versions%ROWTYPE;
    next_version INTEGER;
    new_version_id UUID;
BEGIN
    SELECT *
    INTO candidate
    FROM provision_version_candidates
    WHERE id = p_candidate_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Candidate not found';
    END IF;

    IF candidate.review_status <> 'APPROVED' THEN
        RAISE EXCEPTION
            'Candidate must be APPROVED before promotion. Current status: %',
            candidate.review_status;
    END IF;

    SELECT *
    INTO current_row
    FROM provision_versions
    WHERE provision_id = candidate.provision_id
      AND is_current = TRUE
    FOR UPDATE;

    SELECT COALESCE(MAX(version_number), 0) + 1
    INTO next_version
    FROM provision_versions
    WHERE provision_id = candidate.provision_id;

    IF current_row.id IS NOT NULL THEN
        UPDATE provision_versions
        SET
            is_current = FALSE,
            valid_to = candidate.proposed_valid_from,
            status = 'superseded'
        WHERE id = current_row.id;
    END IF;

    INSERT INTO provision_versions (
        provision_id,
        version_number,
        legal_text,
        valid_from,
        is_current,
        status,
        created_by_instrument_id,
        supersedes_version_id,
        official_url,
        source_hash,
        official_source_verified,
        verified_at,
        verified_by
    )
    VALUES (
        candidate.provision_id,
        next_version,
        candidate.proposed_text,
        candidate.proposed_valid_from,
        TRUE,
        'active',
        candidate.source_instrument_id,
        current_row.id,
        candidate.official_url,
        candidate.source_hash,
        TRUE,
        now(),
        p_reviewer
    )
    RETURNING id INTO new_version_id;

    IF candidate.source_instrument_id IS NOT NULL THEN
        INSERT INTO amendment_events (
            amending_instrument_id,
            target_provision_id,
            operation,
            effective_from,
            old_version_id,
            new_version_id,
            old_text,
            new_text,
            official_url,
            verified,
            verified_at,
            verified_by
        )
        VALUES (
            candidate.source_instrument_id,
            candidate.provision_id,
            COALESCE(candidate.operation, 'OTHER'),
            candidate.proposed_valid_from,
            current_row.id,
            new_version_id,
            current_row.legal_text,
            candidate.proposed_text,
            candidate.official_url,
            TRUE,
            now(),
            p_reviewer
        );
    END IF;

    UPDATE provision_version_candidates
    SET
        review_status = 'PROMOTED',
        reviewer = p_reviewer
    WHERE id = candidate.id;

    RETURN new_version_id;
END;
$$;

COMMIT;
