# Justor AI pilot package: what to use, where, how, and why

Use this file first. The package has two separate tracks:

1. Project A: closed 10-person pilot app.
2. Project B: Supreme Court case research staging.

Do not mix them before the pilot.

## The short decision

For the 10-person pilot, use only Project A/backend/frontend/release-verifier files.

For 100-200 Supreme Court PDFs and case-to-JSON, use only the Project B case pipeline. Keep it disconnected from the pilot app.

## What each major file is for

| File/path | Where to use | Why it exists | Use before pilot? |
|---|---|---|---|
| `PASTE_READY_EXECUTION_PACK.md` | Main operator guide | Exact commands in order | Yes |
| `FINAL_2_DAY_HANDOFF.md` | CTO/release owner | GO/NO-GO evidence and schedule | Yes |
| `README.md` | Engineering overview | Explains release boundary | Yes |
| `backend/asgi.py` | Render/backend runtime | Starts the new fail-closed pilot API | Yes |
| `backend/api.py` | Backend API | Exposes only pilot chat and feedback | Yes |
| `backend/service.py` | Backend logic | Deterministic property/status answers | Yes |
| `backend/repositories.py` | Project A Supabase access | Enforces membership, source cards, feedback | Yes |
| `backend/INTEGRATION.md` | Backend engineer | How to deploy the new runtime | Yes |
| `frontend/pilot-api.ts` | Frontend integration | Clean client for `/v1/pilot/chat` and feedback | Yes |
| `frontend/safe-markdown.ts` | Frontend security | Prevents unsafe rendered model output | Yes |
| `frontend/INTEGRATION.md` | Frontend engineer | How to wire the pilot UI safely | Yes |
| `migrations/project_a_*.sql` | Supabase Project A | Pilot users, law cards, telemetry, RLS | Yes |
| `migrations/project_b_*.sql` | Supabase Project B only | Case staging tables | Optional, not app-visible |
| `scripts/verify_release.py` | Release owner | Stops false-green launch | Yes |
| `evaluation/PILOT_ACCEPTANCE.md` | QA/legal/security | Live 14-case acceptance checklist | Yes |
| `legal_sources/pilot_scope_manifest.json` | Legal reviewers | Current pilot legal scope | Yes |
| `prompts/PILOT_PROMPTS.md` | Product/legal | Controlled pilot response wording | Yes |
| `case_pipeline/scbd_downloader.py` | Offline Project B | Download 100-200 official SCBD PDFs | Optional only |
| `case_pipeline/scbd_extract_text.py` | Offline Project B | Extract page text/OCR from PDFs | Optional only |
| `case_pipeline/build_case_inputs.py` | Offline Project B | Prepare trusted prompt input for one case | Optional only |
| `case_pipeline/scbd_case_prompts.md` | Offline Project B | Prompts to convert case text into JSON | Optional only |
| `case_pipeline/scbd_case_schema.json` | Offline Project B | Required JSON structure | Optional only |
| `case_pipeline/run_case_model.py` | Offline Project B | Automated provider-neutral JSON generation | Optional only |
| `case_pipeline/validate_scbd_case.py` | Offline Project B | Verifies quotes/pages/schema after model output | Optional only |

## Project A: closed 10-person pilot

Project A is the actual app users touch.

Use it for:

- invite-only login;
- 5 citizens, 3 law students, 2 lawyers;
- property-only citizen cards;
- exact statute/status responses for students/lawyers;
- feedback and telemetry;
- release evidence.

Do not use it for:

- 100-200 Supreme Court cases;
- raw PDFs;
- case search;
- public signup;
- guest chat;
- tax calculation.

### Project A execution order

From repo root:

```bash
cd /workspace/scratch/c86768e0f453/JustorAi

python -m venv .venv-verify
. .venv-verify/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  -r pilot_release_v1/requirements-pilot.txt \
  -r pilot_release_v1/requirements-scbd.txt \
  -r pilot_release_v1/requirements-verify.txt

npm ci
npm run build

python pilot_release_v1/scripts/verify_release.py \
  --root pilot_release_v1 --static-only
```

Then run Supabase Project A files in this order:

```text
1. migrations/project_a_preflight_audit.sql
2. migrations/project_a_000_legacy_lockdown.sql
3. migrations/project_a_001_invite_pilot.sql
4. migrations/project_a_postflight.sql
```

Deploy the backend using:

```bash
uvicorn pilot_release_v1.backend.asgi:create_app --factory --host 0.0.0.0 --port $PORT
```

Run live acceptance from:

```text
evaluation/PILOT_ACCEPTANCE.md
```

Final release check:

```bash
python pilot_release_v1/scripts/verify_release.py \
  --root pilot_release_v1 \
  --evidence-dir /ABSOLUTE/PATH/TO/RELEASE_EVIDENCE
```

Only `release_ready: true` means the 10-person pilot can start.

## Project B: Supreme Court PDF and case JSON staging

Project B is an offline research database. It is not part of the pilot app.

Use it for:

- downloading official Supreme Court PDFs;
- extracting page text;
- converting cases into machine JSON;
- staging unverified case data;
- lawyer review later.

Do not connect Project B to the public/pilot backend before launch.

### Download 100 PDFs

```bash
cd /workspace/scratch/c86768e0f453/JustorAi
python -m venv .venv-scbd
. .venv-scbd/bin/activate
python -m pip install --upgrade pip
python -m pip install -r pilot_release_v1/requirements-scbd.txt

python pilot_release_v1/case_pipeline/scbd_downloader.py \
  --contact-email research@YOUR-DOMAIN \
  --ad 25 --hcd 75 --root data/scbd \
  --max-file-mb 100 --max-corpus-mb 5000 --max-pages-per-pdf 1200
```

### Download 200 PDFs

```bash
python pilot_release_v1/case_pipeline/scbd_downloader.py \
  --contact-email research@YOUR-DOMAIN \
  --ad 50 --hcd 150 --root data/scbd \
  --max-file-mb 100 --max-corpus-mb 5000 --max-pages-per-pdf 1200
```

### Extract text

```bash
python pilot_release_v1/case_pipeline/scbd_extract_text.py \
  --root data/scbd --limit 200
```

### Convert one case into JSON

Pick a `source_id` from `data/scbd/manifest.jsonl`, then:

```bash
python pilot_release_v1/case_pipeline/build_case_inputs.py \
  SOURCE_ID \
  --root data/scbd \
  --chunk-pages 10
```

Use:

```text
case_pipeline/scbd_case_prompts.md
case_pipeline/scbd_case_schema.json
```

Automated model run:

```bash
PYTHONPATH=$PWD python pilot_release_v1/case_pipeline/run_case_model.py SOURCE_ID \
  --root data/scbd \
  --provider-id YOUR_PROVIDER \
  --model-id YOUR_MODEL_VERSION \
  --privacy-decision LOCAL_ONLY \
  --model-command python /ABSOLUTE/PATH/model_adapter.py
```

Validate:

```bash
python pilot_release_v1/case_pipeline/validate_scbd_case.py \
  data/scbd/model_outputs/SOURCE_ID/final.json \
  pilot_release_v1/case_pipeline/scbd_case_schema.json \
  data/scbd/prompt_inputs/SOURCE_ID/trusted_source.json \
  data/scbd/pages/SOURCE_ID.jsonl \
  data/scbd/model_outputs/SOURCE_ID/final.errors.json
```

## Why this separation matters

The pilot must prove trust, not volume. Ten people should see only reviewed,
controlled, source-backed answers.

The 100-200 Supreme Court PDFs are useful for building the future case database,
but downloaded PDFs and model-generated JSON are not automatically verified law.
They must stay in staging until the validator and human reviewers approve them.

## What to tell the team

Use `Project A` to launch the closed pilot.

Use `Project B` to build the Supreme Court case dataset in parallel.

Do not expose case search, tax calculation, guest chat, public signup, uploads,
or unreviewed AI case summaries before the 10-person pilot.

