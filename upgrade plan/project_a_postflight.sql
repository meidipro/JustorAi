-- Project A: run after migration and again after participant/legal provisioning.
-- Save the complete output as release evidence. Every query marked ZERO ROWS
-- is a hard gate; cohort/card counts are checked against the launch manifest.

SELECT current_database() AS database_name,
       current_user AS checked_by,
       now() AS checked_at;

SELECT c.relname AS table_name,
       c.relrowsecurity AS rls_enabled,
       c.relforcerowsecurity AS force_rls
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p')
  AND c.relname LIKE 'pilot_%'
ORDER BY c.relname;

-- ZERO ROWS: every backend-only pilot table must have RLS enabled even though
-- the web service also uses narrow SQL grants.
SELECT c.relname AS table_without_rls
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p')
  AND c.relname LIKE 'pilot_%'
  AND NOT c.relrowsecurity;

-- ZERO ROWS: no browser role may access pilot tables or runtime views.
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND table_name LIKE 'pilot_%'
  AND grantee IN ('PUBLIC', 'anon', 'authenticated')
ORDER BY table_name, grantee, privilege_type;

-- ZERO ROWS: the launch browser must not retain the legacy conversation path.
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND table_name IN ('chats', 'messages', 'message_feedback')
  AND grantee IN ('PUBLIC', 'anon', 'authenticated')
ORDER BY table_name, grantee, privilege_type;

-- ZERO ROWS: browser roles may not execute any pilot function.
SELECT grantee, routine_name, privilege_type
FROM information_schema.role_routine_grants
WHERE routine_schema = 'public'
  AND routine_name LIKE 'pilot_%'
  AND grantee IN ('PUBLIC', 'anon', 'authenticated')
ORDER BY routine_name, grantee;

-- Review explicitly. No pilot table should have a browser or allow-all policy.
SELECT schemaname, tablename, policyname, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename LIKE 'pilot_%'
ORDER BY tablename, policyname;

-- ZERO ROWS: canonical section path must round-trip exactly.
SELECT id, act_code, section_root, subsection_path, section_canonical
FROM public.pilot_provision_versions
WHERE section_canonical <> section_root || array_to_string(
    ARRAY(SELECT '(' || item || ')' FROM unnest(subsection_path) AS item), ''
);

-- ZERO ROWS: no citizen-visible provision may bypass source and lawyer review.
SELECT s.provision_id
FROM public.pilot_scope_provisions s
JOIN public.pilot_provision_versions p ON p.id = s.provision_id
JOIN public.pilot_legal_sources src ON src.id = p.source_id
WHERE s.approved_for_citizen
  AND (
      s.approved_by IS NULL OR s.approved_at IS NULL
      OR (s.expires_at IS NOT NULL AND s.expires_at <= now())
      OR NOT p.is_current OR p.legal_status <> 'ACTIVE'
      OR p.verification_status <> 'HUMAN_REVIEWED'
      OR src.verification_status <> 'HUMAN_REVIEWED'
  );

-- ZERO ROWS: active participants require live consent and an unexpired window.
SELECT user_id, display_mode, capabilities, consent_version, expires_at
FROM public.pilot_memberships
WHERE status = 'active'
  AND (
      NOT research_consent
      OR NULLIF(BTRIM(consent_version), '') IS NULL
      OR activated_at IS NULL
      OR expires_at IS NULL
      OR expires_at <= now()
  );

-- ZERO ROWS for every invite wave: capabilities must match the approved role
-- templates, with case_search disabled until a separate reviewed-case gate.
SELECT user_id, display_mode, capabilities
FROM public.pilot_memberships
WHERE status = 'active'
  AND (
      'case_search' = ANY(capabilities)
      OR (display_mode = 'citizen' AND capabilities <> ARRAY['citizen_chat']::text[])
      OR (display_mode = 'student' AND capabilities <> ARRAY['citizen_chat', 'student_research']::text[])
      OR (display_mode = 'lawyer' AND capabilities <> ARRAY['citizen_chat', 'student_research', 'lawyer_research']::text[])
  );

-- Launch evidence: inspect cohort counts and consent versions. First dry-run
-- target is citizen=5, student=3, lawyer=2 and total=10. Later admin-invite
-- waves may exceed 10, but still require active consent and safe capabilities.
SELECT display_mode, count(*) AS active_memberships,
       array_agg(DISTINCT consent_version ORDER BY consent_version) AS consent_versions,
       min(expires_at) AS earliest_expiry
FROM public.pilot_memberships
WHERE status = 'active'
GROUP BY display_mode
ORDER BY display_mode;

SELECT count(*) AS active_total
FROM public.pilot_memberships
WHERE status = 'active';

-- ZERO ROWS: the web service cannot mutate reviewed legal/capability records or
-- delete any pilot record. Human promotion remains an owner operation.
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND grantee = 'service_role'
  AND (
      privilege_type = 'DELETE'
      OR (
          privilege_type IN ('INSERT', 'UPDATE')
          AND table_name IN (
              'pilot_memberships', 'pilot_source_candidates',
              'pilot_legal_sources', 'pilot_provision_versions',
              'pilot_scope_provisions', 'pilot_answer_cards',
              'pilot_answer_card_evidence', 'pilot_legal_status_overrides',
              'pilot_status_cards'
          )
      )
  )
ORDER BY table_name, privilege_type;

-- ZERO ROWS: service_role may execute the rate limiter, but never the owner-only
-- retention function or another pilot mutation function.
SELECT grantee, routine_name, privilege_type
FROM information_schema.role_routine_grants
WHERE routine_schema = 'public'
  AND grantee = 'service_role'
  AND routine_name LIKE 'pilot_%'
  AND routine_name <> 'pilot_check_rate_limit';

-- ZERO ROWS: a human-reviewed card that is not runtime-visible needs correction
-- or explicit retirement before launch; do not assume review status is enough.
SELECT c.id, c.card_code, c.version, c.language, c.workflow_code
FROM public.pilot_answer_cards c
LEFT JOIN public.pilot_runtime_answer_cards r ON r.id = c.id
WHERE c.review_status = 'HUMAN_REVIEWED' AND r.id IS NULL;

-- Launch evidence: ten signed property cards (for the approved language set)
-- and reviewed runtime provisions/status cards as expected by the legal manifest.
SELECT
    (SELECT count(*) FROM public.pilot_runtime_answer_cards) AS runtime_answer_cards,
    (SELECT count(*) FROM public.pilot_runtime_provisions) AS runtime_provisions,
    (SELECT count(*) FROM public.pilot_runtime_status_cards) AS runtime_status_cards;

-- ZERO ROWS: raw/redacted question content is disabled for this release.
SELECT id, user_id, created_at
FROM public.pilot_query_runs
WHERE query_redacted IS NOT NULL;

-- ZERO ROWS: citizen isolation and run lifecycle integrity.
SELECT id, user_id, resolved_mode, case_retrieval_used, run_status,
       decision, decision_reason, finalized_at, error_code
FROM public.pilot_query_runs
WHERE (resolved_mode = 'citizen' AND case_retrieval_used)
   OR (run_status = 'STARTED' AND created_at < now() - interval '15 minutes')
   OR (run_status IN ('FINALIZED', 'ERROR') AND finalized_at IS NULL);

-- Retention evidence. Rows older than the configured 1–90 day period must be
-- purged by the database owner with pilot_purge_telemetry(retention_days).
SELECT min(created_at) AS oldest_query_run,
       max(created_at) AS newest_query_run,
       count(*) AS query_run_count
FROM public.pilot_query_runs;
