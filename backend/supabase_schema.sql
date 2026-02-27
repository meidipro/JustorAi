-- ==========================================================
-- JustorAI RAG Brain — Supabase Schema
-- Run this in Supabase Dashboard > SQL Editor > New Query
-- ==========================================================

-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. Documents table
create table if not exists public.documents (
    id          uuid primary key default gen_random_uuid(),
    title       text not null,
    content     text,
    metadata    jsonb default '{}'::jsonb,
    created_at  timestamp with time zone default timezone('utc', now()) not null
);

-- 3. Document chunks table (384-dim for all-MiniLM-L6-v2)
create table if not exists public.document_chunks (
    id          uuid primary key default gen_random_uuid(),
    document_id uuid references public.documents(id) on delete cascade not null,
    content     text not null,
    embedding   vector(384),
    chunk_index integer not null,
    metadata    jsonb default '{}'::jsonb,
    created_at  timestamp with time zone default timezone('utc', now()) not null
);

-- 4. HNSW index for fast cosine similarity search
create index if not exists document_chunks_embedding_idx
    on public.document_chunks
    using hnsw (embedding vector_cosine_ops);

-- 5. Similarity search RPC function
create or replace function match_document_chunks (
    query_embedding vector(384),
    match_threshold float default 0.5,
    match_count     int   default 5
)
returns table (
    id          uuid,
    document_id uuid,
    content     text,
    metadata    jsonb,
    similarity  float
)
language sql stable
as $$
    select
        dc.id,
        dc.document_id,
        dc.content,
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) as similarity
    from public.document_chunks dc
    where 1 - (dc.embedding <=> query_embedding) > match_threshold
    order by dc.embedding <=> query_embedding
    limit match_count;
$$;

-- 6. Row Level Security
alter table public.documents       enable row level security;
alter table public.document_chunks enable row level security;

-- Drop first to avoid conflicts when re-running this script
drop policy if exists "public read documents"       on public.documents;
drop policy if exists "public read document_chunks" on public.document_chunks;

-- Allow anon (frontend) to read; backend uses service role key which bypasses RLS
create policy "public read documents"
    on public.documents for select to anon using (true);

create policy "public read document_chunks"
    on public.document_chunks for select to anon using (true);
