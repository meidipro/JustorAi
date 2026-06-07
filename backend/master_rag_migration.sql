-- ==========================================================
-- JustorAI Master RAG Deployment — Database Migrations
-- Run this block in the Supabase Dashboard SQL Editor
-- ==========================================================

-- 1. Replace match_acts_v2 with Act-Aware Search logic
create or replace function match_acts_v2(
  query_embedding vector(768),
  match_count int default 8,
  match_threshold float default 0.40,
  query_section text default null,
  prefer_dead_law boolean default false,
  prefer_amended boolean default false,
  filter_act_name text default null
)
returns table (
  id uuid, document_type text, act_name text, section_number text,
  section_title text, status text, jurisdiction text, content text,
  repealed_clauses jsonb, amendment_notes jsonb,
  similarity float, final_score float
)
language sql stable
as $$
  with scored as (
    select
      dc.id, dc.document_type, dc.act_name, dc.section_number,
      dc.section_title, dc.status, dc.jurisdiction, dc.content,
      dc.repealed_clauses, dc.amendment_notes,
      1 - (dc.embedding <=> query_embedding) as similarity,
      (
        (1 - (dc.embedding <=> query_embedding)) * 0.72
        -- Active and Amended are BOTH current law -> equal boost.
        + case
            when lower(dc.status) = 'active'  then 0.20
            when lower(dc.status) = 'amended' then 0.20
            when lower(dc.status) in ('repealed','omitted','deleted')
                 and prefer_dead_law = true then 0.08
            when lower(dc.status) in ('repealed','omitted','deleted') then -0.25
            else 0.00
          end
        -- Exact section-number match
        + case
            when query_section is not null
                 and lower(coalesce(dc.section_number,'')) = lower(query_section)
            then 0.20 else 0.00
          end
        -- Soft act-name match (strong, not a hard gate)
        + case
            when filter_act_name is not null
                 and ( lower(dc.act_name) like '%' || lower(filter_act_name) || '%'
                    or lower(filter_act_name) like '%' || lower(dc.act_name) || '%' )
            then 0.30 else 0.00
          end
      ) as final_score
    from document_chunks dc
    where dc.document_type = 'Act'
      and lower(coalesce(dc.jurisdiction,'')) = 'bangladesh'
      and (1 - (dc.embedding <=> query_embedding)) >= match_threshold
      and (query_section is null
           or lower(coalesce(dc.section_number,'')) = lower(query_section))
  )
  select id, document_type, act_name, section_number, section_title,
         status, jurisdiction, content, repealed_clauses, amendment_notes,
         similarity, final_score
  from scored
  order by final_score desc, similarity desc
  limit match_count;
$$;


-- 2. Create the Telemetry Log Table (pilot_query_log)
create table if not exists pilot_query_log (
  id uuid default gen_random_uuid() primary key,
  created_at timestamptz default now(),
  user_id text, persona text, query text,
  act_detected text, section_detected text,
  sources_found integer default 0,
  retrieval_status text, model_used text,
  response_preview text,
  feedback text default null, feedback_note text default null
);

-- 3. Create indexes for performance optimization
create index if not exists pilot_log_created_idx on pilot_query_log (created_at desc);
create index if not exists pilot_log_status_idx  on pilot_query_log (retrieval_status);

-- 4. Enable Row Level Security and add access policy
alter table pilot_query_log enable row level security;

-- Create policy allowing full read/write access under service role
do $$
begin
  if not exists (
    select 1 from pg_policies 
    where tablename = 'pilot_query_log' and policyname = 'service_role_full_access'
  ) then
    create policy "service_role_full_access" on pilot_query_log for all using (true);
  end if;
end
$$;
