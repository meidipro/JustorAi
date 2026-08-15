-- MIGRATION SCRIPT FOR BAAI/BGE-M3 (1024 dimensions)

-- 1. Drop the old functions that depend on the 768-dimension vectors
DROP FUNCTION IF EXISTS match_acts_v2(vector, float, int, text, boolean, boolean, text);
DROP FUNCTION IF EXISTS match_dlrs_v2(vector, float, int);

-- 2. Alter the document_chunks table
-- We have to drop the column and recreate it, which will delete the old embeddings.
ALTER TABLE document_chunks DROP COLUMN IF EXISTS embedding;
ALTER TABLE document_chunks ADD COLUMN embedding vector(1024);

-- 3. (Skipped dlrs table as it does not exist)

-- 4. Recreate match_acts_v2 function
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
  id bigint,
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
    -- Add a small boost if the section number matches the query explicitly
    1 - (dc.embedding <=> query_embedding) + 
      (CASE WHEN query_section IS NOT NULL AND dc.section_number = query_section THEN 0.05 ELSE 0 END) AS similarity
  FROM document_chunks dc
  WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    -- Filter by Act Name if detected by LLM
    AND (filter_act_name IS NULL OR dc.act_name ILIKE '%' || filter_act_name || '%')
  ORDER BY dc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- 5. (Skipped match_dlrs_v2 as the dlrs table does not exist)
