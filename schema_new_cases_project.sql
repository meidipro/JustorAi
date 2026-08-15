-- ==========================================================
-- Justor AI — New Supabase Project: Cases & DLR Database
-- Run this single block in the SQL Editor of your NEW Supabase project
-- ==========================================================

-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. Create case_chunks table for Supreme Court & DLRs
create table if not exists public.case_chunks (
    id uuid primary key default gen_random_uuid(),
    case_id text unique,                  -- e.g. 'SCBD-AD-2018-001'
    case_title text not null,             -- e.g. 'Abdul Jalil vs Md. Joynal Abedin'
    citation text,                        -- e.g. '67 DLR (AD) 142'
    court_division text not null,         -- 'Appellate Division' or 'High Court Division'
    year int,
    judgment_date text,
    bench_judges text[],
    subject_area text,                    -- e.g. 'Property & Land Law'
    governing_statutes jsonb default '[]'::jsonb,
    ratio_decidendi text not null,        -- The core binding legal ratio
    exact_key_passages jsonb default '[]'::jsonb,
    judgment_content text,                -- Full or summary text
    pdf_source_url text,
    embedding vector(1024),               -- 1024-dim BGE-M3 embedding
    created_at timestamp with time zone default timezone('utc', now()) not null
);

-- 3. High Performance Search Indexes
create index if not exists idx_case_citation on public.case_chunks (citation);
create index if not exists idx_case_division on public.case_chunks (court_division);
create index if not exists idx_case_subject on public.case_chunks (subject_area);
create index if not exists idx_case_year on public.case_chunks (year);

-- 4. Case & DLR Vector Search RPC function
create or replace function match_dlrs_v2(
  query_embedding vector(1024),
  match_count int default 4,
  match_threshold float default 0.30,
  filter_division text default null
)
returns table (
  id uuid,
  case_id text,
  case_title text,
  citation text,
  court_division text,
  year int,
  subject_area text,
  ratio_decidendi text,
  exact_key_passages jsonb,
  judgment_content text,
  pdf_source_url text,
  similarity float
)
language sql stable
as $$
  select
    c.id,
    c.case_id,
    c.case_title,
    c.citation,
    c.court_division,
    c.year,
    c.subject_area,
    c.ratio_decidendi,
    c.exact_key_passages,
    c.judgment_content,
    c.pdf_source_url,
    1 - (c.embedding <=> query_embedding) as similarity
  from public.case_chunks c
  where (1 - (c.embedding <=> query_embedding)) >= match_threshold
    and (filter_division is null or lower(c.court_division) = lower(filter_division))
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
