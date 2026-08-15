# Closed-pilot operations, deployment, and rollback

This runbook does not authorize a launch. Record an owner, timestamp, command or
dashboard action, and evidence location for every gate. Stop on an uncertain
project, missing backup, unexpected grant/policy, stale legal source, or failed
test.

## 1. Freeze the candidate

The current workspace contains unrelated pre-existing edits. Isolate and review
the pilot diff before making an immutable commit. The release record must bind:

- git commit SHA;
- Project A reference and backup identifier;
- dataset, prompt, router, consent, and acceptance-matrix versions;
- frontend/backend deployment identifiers and origins;
- named release owner and two legal reviewers.

Never roll forward base commit `83638f2` or `backend.backend:app`. The tracked
deployment command must start `pilot_release_v1.backend.asgi:create_app`.

## 2. Verify the package

```bash
python -m venv .venv-verify
. .venv-verify/bin/activate
python -m pip install \
  -r pilot_release_v1/requirements-pilot.txt \
  -r pilot_release_v1/requirements-scbd.txt \
  -r pilot_release_v1/requirements-verify.txt
npm ci
python pilot_release_v1/scripts/verify_release.py \
  --root pilot_release_v1 --static-only
```

Archive the JSON output. Static mode is never a GO decision. Do not add a skip,
convert a missing dependency to a warning, or mark a live check PASS without
fresh evidence.

## 3. Project A database gate

In the Supabase dashboard, independently confirm the Project A reference and a
restorable backup/export. Disable public account creation and review redirect
origins/providers. Then execute and save output in this order:

1. `migrations/project_a_preflight_audit.sql`
2. `migrations/project_a_000_legacy_lockdown.sql`
3. `migrations/project_a_001_invite_pilot.sql`
4. `migrations/project_a_postflight.sql`

Do not continue if preflight identifies an unexpected browser grant, allow-all
policy, editable authorization field, permissive future-object ACL, unknown
embedding contract, or mixed dimensions. Every Project A postflight query marked
`ZERO ROWS` must be empty.

The migrations seed candidates and reviewed legal-status facts only. They do
not approve a source, provision, translation, scope row, or answer card. Corpus
promotion is an owner/human workflow; the web service key has no legal-corpus
write grant.

## 4. Legal review and account allocation

Two people independently follow `legal_sources/LEGAL_QA.md`. At least one is the
lawyer responsible for final entailment review. Every visible statement and
limitation needs an exact quote-bound evidence row. Confirm the 2026 Registration
Act amendments and section 23/24–26 distinctions from the official current law.

Create accounts through a controlled Project A pilot flow only: administrative
invite, email allowlist, or a one-time invite code. Open public signup remains
disabled, but accounts are required so data, consent, query runs, and feedback
attach to a verified Auth UUID. After invitation acceptance and approved
consent, insert one membership per verified Auth UUID. Example:

```sql
INSERT INTO public.pilot_memberships (
    user_id, status, display_mode, capabilities, research_consent,
    consent_version, activated_at, expires_at, created_by
) VALUES (
    'PARTICIPANT_AUTH_UUID',
    'active',
    'citizen',
    ARRAY['citizen_chat']::text[],
    true,
    'APPROVED_CONSENT_VERSION',
    now(),
    now() + interval '14 days',
    'OPERATOR_AUTH_UUID'
);
```

First-wave dry-run allocation:

| Cohort | Count | Capabilities |
|---|---:|---|
| Citizen | 5 | `citizen_chat` |
| Student | 3 | `citizen_chat`, `student_research` |
| Lawyer | 2 | `citizen_chat`, `student_research`, `lawyer_research` |

No launch participant receives `case_search`, `corpus_admin`, or `pilot_admin`.
Do not infer access from email domain, user metadata, editable profile fields, or
the frontend mode selector. Rerun Project A postflight after provisioning; for
the first dry run, its cohort output should show 5/3/2 and total 10 with one
current consent version. After GO, expand only by named admin-invite batches and
monitor the same cohort/capability output instead of treating 10 as a product
cap.

## 5. Participant notice

Local counsel must approve the exact notice and retention/incident terms. It
must state that this is a limited monitored research pilot; it is not a lawyer,
legal representation, or legal advice; content can be incomplete or wrong; and
participants should check official sources and consult a qualified Bangladeshi
lawyer before acting.

Tell participants not to enter client names, privileged/confidential facts,
national IDs, phone numbers, exact addresses, dates of birth, bank/account
numbers, credentials, or unnecessary personal data. Voice and document input are
disabled. Chat content stays in browser memory; the backend stores a keyed HMAC
and release/decision telemetry, not question text.

## 6. Backend deployment

Configure only these backend values. Do not use a `VITE_` prefix for a secret.

```text
JUSTOR_PROJECT_A_URL
JUSTOR_PROJECT_A_ANON_KEY
JUSTOR_PROJECT_A_SERVICE_ROLE_KEY
JUSTOR_ALLOWED_ORIGINS
JUSTOR_APP_COMMIT
JUSTOR_DATASET_VERSION
JUSTOR_PROMPT_VERSION
JUSTOR_ROUTER_VERSION
JUSTOR_QUERY_HMAC_KEY
JUSTOR_CONSENT_VERSION
JUSTOR_TELEMETRY_RETENTION_DAYS
```

Keep all safe flags at the values in `.env.pilot.example`; in particular,
`ENABLE_CASE_RETRIEVAL=false`. Do not configure Project B or model-provider keys
in the launch web service. Generate the HMAC key independently with at least 32
random bytes; do not reuse a JWT or Supabase key.

The deployment must use the exact tracked build/start commands. Put the service
behind HTTPS and, for a closed pilot, an upstream access restriction. Verify the
public route map contains only `/v1/pilot/chat` and `/v1/pilot/feedback` business
routes and that the legacy origin/process is unreachable.

## 7. Frontend deployment

Configure only:

```text
VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY
VITE_BACKEND_URL
```

Run `npm ci && npm run build`. Inspect built assets and source maps for secrets.
At the deployed origin, verify CSP/security headers, sign-in-only behavior,
protected routes, no guest entry, no open public signup/OAuth creation, no
legacy database requests, sanitized adversarial Markdown, official source-link
allowlisting, and feedback ownership. The Auth dashboard must independently
reject open public signup even if a
caller bypasses the UI.

## 8. Live acceptance and dry run

Copy `evaluation/live_acceptance_results.example.json` to the release-evidence
directory. For every live ID, record a real environment, timestamp, and evidence
reference. Execute the strict verifier with that directory. A filled template is
not evidence; the named owner must inspect the referenced logs/screenshots/query
results.

Use all ten accounts in a monitored scripted dry run. Confirm capability denial,
consent/expiry, official sources, deterministic card behavior, safe abstention,
rate limits (10 chat/minute and 100/day), feedback ownership, and zero citizen
case retrieval.

## 9. Telemetry and retention

Monitor authentication failures, 403/429/5xx rates, abstention changes,
unfinalized runs, source-card anomalies, feedback linkage, and
`case_retrieval_used`. Any citizen run with that flag true is severity one and an
automatic NO-GO.

After counsel approves a 1–90 day retention period, schedule the database owner
to run the matching value. This is destructive and cascades to run evidence and
feedback, so retain only the separately approved release/incident evidence:

```sql
SELECT public.pilot_purge_telemetry(30) AS query_runs_deleted;
```

The web service cannot execute this function. Rerun the retention section of
Project A postflight and preserve the aggregate result, not deleted question
content.

## 10. Optional Project B staging

Project B must be a different confirmed project with its own backup. Apply only
`project_b_001_case_staging.sql`, then run `project_b_postflight.sql`. The web
service remains disconnected.

Before any batch, install approved Bengali and English Tesseract language data
and prove `tesseract --list-langs` includes `eng` and `ben`. Run the two-document
AD/HCD smoke sequence in `case_pipeline/README.md`, inspect snapshots/PDFs/pages,
and only then consider 100–200 downloads. Weak OCR stays `ocr_low_quality` /
`NEEDS_OCR`. Generated JSON cannot promote itself. Source verification and pilot
legal approval require distinct registered humans, page-bound passages, and
clean postflight output.

## Immediate stop and rollback

1. Set case/upload/admin/eval/MCP flags false and stop routing traffic to the
   deployment. Do not roll back to the legacy monolith.
2. Suspend access (reversible):

```sql
UPDATE public.pilot_memberships
SET status = 'suspended', updated_at = now()
WHERE status = 'active';
```

3. Rotate any key that may have reached a browser, log, chat, repository, or
   unapproved operator. Rebuild from clean secret values.
4. Preserve minimum necessary incident evidence, identify affected query-run
   IDs, notify the named owner/counsel, correct the defect, and rerun every gate.
5. Require a new signed GO/NO-GO. Rollback means access shutdown and a reviewed
   forward fix; do not drop pilot tables or erase the audit trail unless the
   approved privacy/legal process specifically requires it.
