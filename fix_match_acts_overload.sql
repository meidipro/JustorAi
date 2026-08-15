-- FIX OVERLOADED RPC FUNCTION IN SUPABASE (Updated id to UUID)
-- Run this in your Supabase SQL Editor

-- 1. Drop existing match_acts_v2 signatures
DROP FUNCTION IF EXISTS match_acts_v2(vector, integer, double precision, text, boolean, boolean, text);
DROP FUNCTION IF EXISTS match_acts_v2(vector, double precision, integer, text, boolean, boolean, text);
DROP FUNCTION IF EXISTS match_acts_v2(vector, integer, double precision, text, boolean, boolean);
DROP FUNCTION IF EXISTS match_acts_v2(vector, double precision, integer, text, boolean, boolean);

-- 2. Create match_acts_v2 function with id uuid
CREATE OR REPLACE FUNCTION match_acts_v2(
  query_embedding vector(1024),
  match_threshold float,
  match_count int,
  query_section text DEFAULT NULL,
  prefer_dead_law boolean DEFAULT false,
  prefer_amended boolean DEFAULT false,
  filter_act_name text DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  document_id uuid,
  act_name text,
  section_number text,
  section_title text,
  content text,
  status text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    dc.id,
    dc.document_id,
    dc.act_name,
    dc.section_number,
    dc.section_title,
    dc.content,
    dc.status,
    (1 - (dc.embedding <=> query_embedding)) + 
      (CASE WHEN query_section IS NOT NULL AND dc.section_number = query_section THEN 0.05 ELSE 0 END) AS similarity
  FROM document_chunks dc
  WHERE (1 - (dc.embedding <=> query_embedding)) > match_threshold
    AND (filter_act_name IS NULL OR dc.act_name ILIKE '%' || filter_act_name || '%')
  ORDER BY dc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
