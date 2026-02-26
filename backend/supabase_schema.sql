-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Table to store high-level document metadata
create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    content text not null, -- The full original text (optional, but good for reference)
    metadata jsonb default '{}'::jsonb, -- e.g., author, date, source URL, legal topic
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Table to store document chunks and their embeddings
create table if not exists public.document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid references public.documents(id) on delete cascade not null,
    content text not null, -- The specific chunk of text
    embedding vector(1024), -- The embedding vector (size depends on the model, e.g., 1536 for OpenAI, 1024 for BGE-m3, adjust as needed)
    chunk_index integer not null, -- To maintain the order of chunks
    metadata jsonb default '{}'::jsonb, -- Metadata specific to this chunk (e.g., page number)
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create a generic function to perform similarity search
-- This function can be called via Supabase RPC (Remote Procedure Call) from the backend
create or replace function match_document_chunks (
  query_embedding vector(1024), -- Must match the vector size in document_chunks
  match_threshold float,
  match_count int,
  filter_metadata jsonb default '{}'::jsonb
)
returns table (
  id uuid,
  document_id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select
    document_chunks.id,
    document_chunks.document_id,
    document_chunks.content,
    document_chunks.metadata,
    1 - (document_chunks.embedding <=> query_embedding) as similarity
  from document_chunks
  where 1 - (document_chunks.embedding <=> query_embedding) > match_threshold
    and document_chunks.metadata @> filter_metadata -- Optional metadata filtering
  order by document_chunks.embedding <=> query_embedding
  limit match_count;
$$;

-- Create an index to speed up vector similarity searches
-- ivfflat or hnsw can be used. HNSW is generally recommended for better recall and performance in pgvector >= 0.5.0
create index if not exists document_chunks_embedding_idx on public.document_chunks using hnsw (embedding vector_cosine_ops);

-- Set Row Level Security (RLS) policies if needed
-- For a backend service (FastAPI) connecting with a service role key, RLS can be bypassed,
-- but it's good practice to secure tables.

-- Example: Allow read access to authenticated users
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;

create policy "Allow read access to authenticated users" on public.documents
    for select to authenticated using (true);

create policy "Allow read access to authenticated users" on public.document_chunks
    for select to authenticated using (true);

-- (Backend should use the Service Role Key to insert/update/delete, which bypasses RLS)
