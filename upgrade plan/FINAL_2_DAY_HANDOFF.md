# Justor AI closed-pilot handoff

**Decision date:** 2026-08-12  
**Decision:** **NO-GO for participant launch**  
**Reviewed scope:** invite-only pilot for 5 citizens, 3 law students, and 2 lawyers

The engineering package is statically valid, but the release is not deployed,
the ten legal cards have not been approved in the live database, and no fresh
live acceptance evidence has been supplied. Do not describe this as production
ready, 90% accurate, or 90% complete.

## Verified workspace evidence

| Gate | Result |
|---|---:|
| Python unit tests | 34 passed; 0 failed; 0 skipped |
| Executable acceptance checks | 27/27 passed |
| Live acceptance evidence | 0/14 supplied |
| SQL syntax | 6/6 files parsed with `pglast==7.7` |
| Frontend production build | passed |
| npm audit, runtime and build graph | 0 vulnerabilities |
| Pinned Python dependencies | matched; `pip check` clean |
| Tesseract | `eng` and `osd` present; **`ben` missing** |
| Verifier `package_valid` | `true` |
| Verifier `release_ready` | **`false`** |
| Whitespace/error check | `git diff --check` passed |

The strict verifier exits nonzero for exactly two unresolved categories in this
workspace: missing Bengali OCR data and missing live evidence. Static success
does not prove live Supabase state, Auth settings, deployed routes/headers,
legal approval, consent, or participant isolation.

## Source-control state

- Branch: `main`
- Base `HEAD`: `83638f2a8a2029d16c2232a1bc4f185f865f59ff`
- State: mixed, uncommitted working tree
- Deployment rule: never deploy the base SHA; it starts the legacy backend.

Before staging a commit, separate and owner-review unrelated working-tree edits,
including the benchmark, legacy Supreme Court tooling, staging schema, and
`pilot_implementation/`. Stage only the reviewed pilot release surface, inspect
the complete staged diff, then push one immutable commit. Put that exact SHA in
`JUSTOR_APP_COMMIT` and in the release evidence.

## Implemented safety boundary

- The deployment starts the closed pilot ASGI app, not the legacy monolith.
- Chat and feedback require a valid Project A user, active invite membership,
  current consent version, unexpired access, and backend-owned capability.
- Citizen answers are property-only and deterministic from currently effective,
  lawyer-reviewed cards. Student/lawyer output is exact reviewed statutory text.
  Tax is clarify-or-abstain and never supplies a substantive numeric answer.
- Case retrieval is disabled. Project B is separate offline staging and is not a
  launch dependency.
- Project A SQL revokes browser access to legacy chat tables, restricts corpus
  mutation, minimizes telemetry, verifies feedback ownership, enforces shared
  minute/day limits, and supplies an owner-only retention purge.
- The browser has no guest/signup, OAuth account creation, uploads, document or
  case tools, voice, third-party scripts, or browser keep-alive. Model Markdown
  crosses a DOMPurify allowlist; official-source links are constructed from
  trusted metadata.
- The SCBD job has a 200-document cap, PDF/page validators, resumability,
  English+Bengali OCR preflight, weak-OCR staging, quote/page/hash validation,
  and two-distinct-reviewer promotion controls.
- The verifier executes tests and acceptance code, parses every migration,
  builds the frontend, checks exact dependency pins, and runs a current npm
  registry audit. Missing tools, skipped tests, unavailable audit data, stale
  evidence, and placeholder evidence all fail closed.

## Mandatory path to a GO decision

Complete these steps in order. A failure at any step is a NO-GO.

1. **Freeze source.** Isolate the intended changes, review the staged diff,
   create and push an immutable commit, and record its SHA.
2. **Prepare Project A.** Confirm the exact project reference, take and test a
   restorable backup, disable public sign-up, and archive the output of
   `migrations/project_a_preflight_audit.sql`.
3. **Migrate Project A.** Apply
   `project_a_000_legacy_lockdown.sql`, then
   `project_a_001_invite_pilot.sql`. Run and archive
   `project_a_postflight.sql`; every exception/zero-row gate must pass.
4. **Approve current law.** Two named lawyers must independently review the ten
   property provisions, companions, official evidence, translations,
   effective/superseded dates, and all ten runtime cards. Candidate or model
   output is never approval.
5. **Provision exactly ten people.** Invite 5 citizens, 3 students, and 2
   lawyers. Record counsel-approved consent, exact consent version, cohort
   capability, activation, and expiry. Keep `case_search` absent.
6. **Deploy the frozen SHA.** Configure only documented variables, prove the
   new ASGI origin is live, prove legacy origins/routes are unreachable, verify
   CORS and security headers, and scan built assets for secrets.
7. **Run live acceptance.** Execute all 14 procedures in
   `evaluation/PILOT_ACCEPTANCE.md`. Each result must name the environment and
   human tester, include concrete evidence, be `PASS`, and be no more than 24
   hours old when the strict verifier runs.
8. **Dry run and sign.** Exercise all ten accounts. A named release owner and
   both legal reviewers inspect the evidence and sign a fresh GO/NO-GO record.

The 14 live IDs are `AUTH-001` through `AUTH-004`, `SEC-004`, `SEC-005`,
`LEGAL-001`, `LEGAL-003`, `LEGAL-004`, `CASE-002`, `CASE-005`, `CASE-006`,
`TEL-002`, and `TEL-003`.

## Reproducible verification

Run in an isolated QA environment with Python 3.12.13 and current npm registry
access:

```bash
python -m venv .venv-verify
. .venv-verify/bin/activate
python -m pip install \
  -r pilot_release_v1/requirements-pilot.txt \
  -r pilot_release_v1/requirements-scbd.txt \
  -r pilot_release_v1/requirements-verify.txt
python -m pip check
npm ci
python pilot_release_v1/scripts/verify_release.py \
  --root pilot_release_v1 --static-only
```

Install Bengali Tesseract data in the QA/SCBD environment and verify both
`eng` and `ben` appear in `tesseract --list-langs`. After recording live
results in the evidence directory, run the release gate without
`--static-only`:

```bash
python pilot_release_v1/scripts/verify_release.py \
  --root pilot_release_v1 \
  --evidence-dir /ABSOLUTE/PATH/TO/RELEASE_EVIDENCE
```

Only exit code zero with `release_ready: true` supports a GO review.

## Two-day execution window

| Window | Owner | Exit condition |
|---|---|---|
| Day 1, 0–2 h | Engineering/security | Clean reviewed commit; verifier reproducible |
| Day 1, 2–4 h | Project A owner | Backup, preflight, migrations, postflight all archived |
| Day 1, 4–10 h | Two lawyers + students | Ten current-law sources/cards independently signed |
| Day 1, 10–12 h | Backend/deployment | New SHA live; legacy backend unavailable |
| Day 2, 0–3 h | Frontend/security | Headers, CORS, secrets, and XSS evidence captured |
| Day 2, 3–7 h | QA/legal | 14/14 fresh live results PASS |
| Day 2, 7–9 h | Data operator, optional | `ben` installed; two-document SCBD smoke stays staged |
| Day 2, 9–11 h | Ten participants | Consent, capability, expiry, and isolation dry run passes |
| Day 2, 11–12 h | Release owner + lawyers | Evidence reviewed; signed GO/NO-GO |

## Stop and rollback rules

Immediately stop access for any authentication bypass, cross-user data access,
unsafe rendered markup, unreviewed or stale law, incorrect citation/quote/hash,
case leakage, raw sensitive query storage, broken feedback ownership, or rate
limit failure. Disable participant memberships, roll the frontend/backend back
to the last reviewed SHA, preserve audit evidence, and restore the database only
through the Project A owner’s tested backup procedure. Never promote Project B
case data as part of rollback.

Project B remains optional during the two days. If used, verify it is a distinct
project, back it up separately, apply only the Project B migration, run its
postflight, install `eng`+`ben`, smoke-test two documents, and keep the
application disconnected.

## Current-law correction that must be reviewed

The legal manifest now includes the **Registration (Amendment) Act, 2026, Act
No. 14 of 2026**, dated 10 April 2026. It covers the current section 17A
presentation-period change, section 26, expanded section 52A, and new section
77A. Registration Act section 23 itself is three months and must not be
misstated as four months or collapsed into its companion rules.

Official review sources:

- [Registration (Amendment) Act, 2026](https://bdlaws.minlaw.gov.bd/act-1643.html)
- [Current Registration Act section 17A](https://bdlaws.minlaw.gov.bd/act-90/section-22918.html)
- [Current Registration Act section 23](https://bdlaws.minlaw.gov.bd/act-90/section-22926.html)

These links and the package are inputs to lawyer review, not substitutes for it.
