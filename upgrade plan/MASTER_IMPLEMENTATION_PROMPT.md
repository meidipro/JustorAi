# Prompt for the final Justor AI release operator/coding agent

```text
You are finishing an invite-only Bangladesh legal-information research pilot.
Treat pilot_release_v1 as the release contract. Do not broaden scope, claim legal
accuracy from code tests, fabricate live evidence, or deploy the legacy backend.

START
1. Print git SHA, branch, and working-tree status. The base SHA 83638f2 starts
   the old monolith and is not releasable. Preserve unrelated user edits and
   isolate the pilot changes for review before creating a release commit.
2. Read README.md, OPERATIONS.md, backend/INTEGRATION.md,
   frontend/INTEGRATION.md, legal_sources/LEGAL_QA.md, both projects' SQL,
   evaluation/PILOT_ACCEPTANCE.md, and case_pipeline/README.md.
3. Run the static verifier exactly as README.md specifies. Fix genuine failures;
   never weaken a check, add a skip, or convert missing live evidence to PASS.

LAUNCH BOUNDARY
- Admin-invite accounts only. Start with exactly 5 citizens, 3 law students,
  and 2 lawyers for dry-run evidence; after clean GO, expand by named invite
  batches to collect more feedback.
- Project A owns Auth, backend-only memberships/capabilities, reviewed statutes
  and cards, privacy-minimized telemetry, rate limits, and feedback.
- Project B is separate offline case staging and is disconnected at launch.
- The browser may send only message and requested_mode with a Bearer token.
  Identity/capability comes from verified Auth plus pilot_memberships.
- Citizen answers are deterministic lawyer-reviewed property cards only.
- Student/lawyer answers are exact reviewed statutory text/status cards only.
- Tax is non-numeric clarify/abstain-only.
- Case retrieval, uploads, document analysis/admin, guest access, open public
  signup/OAuth self-enrollment, provider/model choice, eval, MCP, and voice are
  all disabled.
- AI-generated case facts/ratio/holding are staging metadata, never approval.
- Official source identity, exact section, date/status, hash, quote, statement
  coverage, and lawyer entailment review are mandatory.

DEPLOYMENT
- Start only pilot_release_v1.backend.asgi:create_app with --factory. Prove the
  old backend process and routes are unreachable.
- Install only requirements-pilot.txt in the web image. Configure only documented
  JUSTOR_* secrets and safe flags; never expose a service key through VITE_*.
- Frontend public variables are only Project A URL/anon key and backend URL.
- Disable open public signup in Project A Auth independently of the UI.
- Keep ENABLE_CASE_RETRIEVAL=false and omit Project B/model-provider credentials.

DATABASE AND LEGAL
1. Confirm the exact Project A dashboard/reference and restorable backup.
2. Save preflight output; stop on unexpected policies/grants/default ACLs/profile
   authority or an unknown vector contract.
3. Apply Project A lockdown then invite migration; save postflight output. Every
   ZERO ROWS query must be empty after legal/account provisioning.
4. Two humans independently check the ten target property provisions, companion
   rules, translations, amendments, dates, statuses, statement quotes, and cards.
   Cover Registration (Amendment) Act 2026, Act No. 14 of 2026; do not collapse
   Registration Act section 23 with sections 24-26.
5. Provision first-wave 5/3/2 capabilities, current consent version and expiry.
   Do not grant case_search/admin capabilities. Later waves use the same safe
   role templates through admin invite.

LIVE GATES
- Execute all 14 live IDs with fresh evidence, including Auth/membership denial,
  shared rate limits, deployed XSS/headers, legal-card behavior, distinct Project
  B isolation, downloader resume, case promotion exclusion, and telemetry owner
  linkage.
- Install eng+ben OCR data and run a two-document AD/HCD smoke before any larger
  optional SCBD batch. Keep every case in staging.
- Run the first ten-account monitored dry run.

RELEASE GATES
- Zero security failures.
- 100% unsupported/adversarial abstention.
- 100% citation/source/hash/quote and feedback ownership integrity.
- 100% citizen-to-Project-B isolation.
- At least 90% scoped routing/exact retrieval on the frozen set.
- Ten lawyer-reviewed runtime property cards and clean first-wave 5/3/2
  accounts; later invite waves are allowed after GO.
- Strict verifier release_ready=true with fresh evidence.
- Named CTO/release owner plus legal reviewers sign GO.

DELIVERABLE
Return the immutable commit and deployment IDs, exact diff summary, Project A
backup/pre/postflight evidence, legal reviewer/card manifest, test counts and
failures, all immutable runtime versions, rollback result, and an explicit
GO/NO-GO. Do not advertise 80%/90% accuracy, production readiness, Harvey-level
quality, or zero hallucinations. The historical ~33% benchmark remains the
baseline until a frozen blinded lawyer-graded evaluation replaces it.
```
