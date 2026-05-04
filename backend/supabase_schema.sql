-- ==========================================================
-- JustorAI RAG Brain — Production Schema (v2)
-- Supports structured legal fields for Acts and DLRs
-- ==========================================================

-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. RESET (Optional/Clean Slate)
-- Un-comment these if you want a completely fresh start (this deletes ALL existing law data)
drop table if exists public.document_chunks cascade;
drop table if exists public.documents cascade;

-- 3. Documents table (Acts and Case Law Collections)
create table if not exists public.documents (
    id          uuid primary key default gen_random_uuid(),
    title       text not null,
    content     text,
    metadata    jsonb default '{}'::jsonb,
    created_at  timestamp with time zone default timezone('utc', now()) not null
);

-- 3. Document chunks table (expanded for explicit legal metadata)
create table if not exists public.document_chunks (
    id                uuid primary key default gen_random_uuid(),
    document_id       uuid references public.documents(id) on delete cascade not null,
    
    -- Core fields
    content           text not null,
    embedding         vector(384), -- Keeping 384 for MiniLM compatibility
    chunk_index       integer not null,
    created_at        timestamp with time zone default timezone('utc', now()) not null,
    
    -- Legal Metadata Fields
    document_type     text,     -- 'Act' or 'DLR'
    jurisdiction      text default 'Bangladesh',
    
    -- Specific to Acts
    act_name          text,
    section_number    text,
    section_title     text,
    status            text,     -- 'Active', 'Repealed', 'Omitted', 'Deleted', 'Amended'
    repealed_clauses  jsonb default '[]'::jsonb,
    amendment_notes   jsonb default '[]'::jsonb,
    
    -- Specific to DLR/Case Law
    case_title        text,
    court_division    text,
    year              text,
    subject_law       text,
    ratio_decidendi   text,
    judgment_content  text,
    
    -- Ranking field
    status_rank       integer default 1, -- Active=3, Amended=2, Dead=1
    
    -- Backward compatibility
    metadata          jsonb default '{}'::jsonb
);

-- 4. HNSW index for fast cosine similarity search
create index if not exists document_chunks_embedding_idx
    on public.document_chunks
    using hnsw (embedding vector_cosine_ops);

-- 5. RPC for Statutory Law (Acts)
create or replace function match_acts_v2(
  query_embedding vector(384),
  match_count int default 6,
  match_threshold float default 0.45,
  query_section text default null,
  prefer_dead_law boolean default false,
  prefer_amended boolean default false
)
returns table (
  id uuid,
  document_type text,
  act_name text,
  section_number text,
  section_title text,
  status text,
  jurisdiction text,
  content text,
  repealed_clauses jsonb,
  amendment_notes jsonb,
  similarity float,
  final_score float
)
language sql stable
as $$
  with scored as (
    select
      dc.id,
      dc.document_type,
      dc.act_name,
      dc.section_number,
      dc.section_title,
      dc.status,
      dc.jurisdiction,
      dc.content,
      dc.repealed_clauses,
      dc.amendment_notes,
      1 - (dc.embedding <=> query_embedding) as similarity,

      (
        (1 - (dc.embedding <=> query_embedding)) * 0.72
        +
        case
          when lower(dc.status) = 'active' then 0.22
          when lower(dc.status) = 'amended' and prefer_amended = true then 0.20
          when lower(dc.status) = 'amended' then 0.16
          when lower(dc.status) in ('repealed','omitted','deleted') and prefer_dead_law = true then 0.08
          when lower(dc.status) in ('repealed','omitted','deleted') then -0.20
          else 0.00
        end
        +
        case
          when query_section is not null and lower(coalesce(dc.section_number,'')) = lower(query_section) then 0.20
          else 0.00
        end
      ) as final_score

    from document_chunks dc
    where dc.document_type = 'Act'
      and lower(coalesce(dc.jurisdiction,'')) = 'bangladesh'
      and (1 - (dc.embedding <=> query_embedding)) >= match_threshold
  )
  select
    id,
    document_type,
    act_name,
    section_number,
    section_title,
    status,
    jurisdiction,
    content,
    repealed_clauses,
    amendment_notes,
    similarity,
    final_score
  from scored
  order by final_score desc, similarity desc
  limit match_count;
$$;

-- 6. RPC for Case Law (DLRs)
create or replace function match_dlrs_v2(
  query_embedding vector(384),
  match_count int default 3,
  match_threshold float default 0.45
)
returns table (
  id uuid,
  document_type text,
  case_title text,
  court_division text,
  year text,
  subject_law text,
  ratio_decidendi text,
  judgment_content text,
  jurisdiction text,
  similarity float
)
language sql stable
as $$
  select
    dc.id,
    dc.document_type,
    dc.case_title,
    dc.court_division,
    dc.year,
    dc.subject_law,
    dc.ratio_decidendi,
    dc.judgment_content,
    dc.jurisdiction,
    1 - (dc.embedding <=> query_embedding) as similarity
  from document_chunks dc
  where dc.document_type = 'DLR'
    and lower(coalesce(dc.jurisdiction,'')) = 'bangladesh'
    and (1 - (dc.embedding <=> query_embedding)) >= match_threshold
  order by similarity desc
  limit match_count;
$$;

-- 7. Row Level Security
alter table public.documents       enable row level security;
alter table public.document_chunks enable row level security;

create policy "public read documents"
    on public.documents for select to anon using (true);

create policy "public read document_chunks"
    on public.document_chunks for select to anon using (true);

