# Justor AI — Five-Day Pilot Execution Command Center

**Prepared:** 10 August 2026  
**Owners:** Tajuddin Ahamed, Mehedi Hasan, AI support  
**Target:** Begin a controlled, announced pilot for a narrow Citizen Mode and a lawyer research mode; collect traceable evidence for the iDEA Startup Grant.

---

## 1. Executive decision

Five days can make Justor **perfectly scoped for the first pilot wave**. It cannot make the whole Bangladesh legal system perfect.

The five-day product is:

1. **Citizen Mode:** verified Bangladesh property and income-tax navigation only.
2. **Lawyer Web Mode:** statute search plus page-level official case passages.
3. **Private MCP prototype:** three read-only research tools using the same backend evidence service.
4. **Two Supabase projects:** Project A for statutes, users, and telemetry; Project B for cases only.
5. **Evidence-first answers:** exact retrieval, current-law/version gates, backend-generated citations, clarification, and abstention.
6. **Controlled rollout:** 10 internal/smoke testers on Day 5, followed by waves toward 20 lawyers, 40 students, and 100 citizens.

The Day 5 announcement should recruit or invite people to a **closed pilot**. It should not open unrestricted public access.

---

## 2. What the repository and attached files establish

### 2.1 Useful assets already exist

- A Vite/TypeScript frontend and FastAPI backend.
- Supabase authentication and chat records in the frontend.
- A large scraped Bangladesh Code corpus.
- Property-law JSON files in the repository.
- A query classifier, persona prompts, law/case RPCs, and benchmark harnesses.
- Supreme Court crawler, downloader, extractor, parser, staging schema, and ingestion scripts.
- A preliminary pilot query log.
- An amendment/version architecture and a public follow-up design.
- A citation/indexing specification for approved official sources.

### 2.2 The broad law corpus is not uniformly production-safe

The supplied audit reports approximately:

- 2,388 scraped JSON files;
- 67,327 raw records;
- 764 redundant file copies;
- status conflicts, taxonomy defects, malformed records, case-law contamination, and unresolved source verification;
- zero fully source-verified Acts in the reported 100-file sample.

Therefore:

> Existing ingestion proves coverage, not verification.

Do not delete the broad corpus. Keep it as raw/staging data. Citizen Mode must query a separate pilot-approved provision registry.

### 2.3 Confirmed critical code defects

1. Exact section lookup uses `%section%` and can retrieve Section 14/40/54 for Section 4.
2. `section_not_exact` is allowed to answer.
3. Case/DLR retrieval runs for every query.
4. Domain filtering restores unsafe results when all results are filtered.
5. Neighbor windowing can reintroduce blocked/dead law.
6. Source objects use `act`, while citation verification reads `act_name`; the verifier usually checks nothing.
7. Citation failure strips a tag and leaves the unsupported legal claim.
8. The law schema/RPC files declare 768-dimensional vectors while `/chat` generates 1024-dimensional BGE-M3 vectors.
9. Different ingestion scripts use Gemini 768, BGE-M3 1024, and Qwen embeddings without one contract.
10. Supreme Court ingestion keeps only the first 10 pages of a judgment.
11. The current promotion tool writes cases into the law table using the case number as `act_name` and page number as `section_number`.
12. `backend/supabase_schema.sql` contains active destructive `DROP TABLE ... CASCADE` statements.
13. CORS is `*`, chat/upload/document endpoints have no backend authentication, and `user_id` is caller-controlled.
14. Markdown from the model is inserted through unsanitized `innerHTML`.
15. README still instructs deployment of browser-prefixed Groq/Dify secrets.
16. The repository contains no MCP server.
17. Feedback is not linked to the exact backend answer/retrieval run.

### 2.4 Baseline verification status

- Python files compile successfully.
- The frontend build was not verifiable in the current checkout because the TypeScript executable was missing from the installed dependency tree. Run `npm ci` before treating the build as passing.
- The earlier “Pilot Launch Ready,” “zero hallucination,” and 75–86% progress report is contradicted by the current code and later human benchmark review. It must not be used in public or grant claims.

---

## 3. Frozen five-day product scope

## 3.1 Citizen Mode: property navigator

### Supported workflows

1. **Sale/transfer preparation**
   - Explain sale versus contract for sale.
   - Identify whether writing/registration is required from verified sections.
   - Provide a general document and authority checklist.

2. **Gift of immovable property**
   - Explain the general statutory form and registration requirement.
   - Identify missing facts and recommend professional confirmation.

3. **Registration navigator**
   - Explain why a document may require registration.
   - Identify the relevant Act/section and official source.
   - Provide a non-exhaustive preparation checklist.

4. **Land-record concept explainer**
   - Explain deed, mutation, khatian, possession, land-development-tax records, and how they differ.
   - Never state that one record conclusively proves title.

5. **Tenancy and co-sharer issue spotting**
   - Ask whether land is agricultural/non-agricultural and whether the person is owner, co-sharer, tenant, buyer, or seller.
   - Identify potentially relevant provisions.
   - Do not calculate a filing deadline unless the exact current authority and triggering date are verified.

6. **Agricultural land ceiling explanation**
   - Explain the verified general rule and the facts that can change the result.
   - Do not issue a title or acquisition opinion.

### Hard abstentions

- Inheritance shares or personal-law calculations.
- Final title opinions.
- Complex partition, vested/abandoned property, adverse possession, and litigation strategy.
- Limitation/deadline calculation without exact current authority and dates.
- Outcome prediction.
- Drafting a deed for execution.

## 3.2 Citizen Mode: tax navigator

### Supported workflows

1. **Do I need to file?**
   - Ask taxpayer type, residency, assessment year, TIN status, relevant assets/registrations, and general income category.
   - Answer only from current Income Tax Act/Finance Act/NBR material stored for that assessment year.

2. **Return and e-return preparation**
   - Provide official process guidance and a document checklist.
   - Link the current NBR form/notice/guidance.

3. **Deadline and current notice lookup**
   - Use current official NBR notices, not a hard-coded date in the model prompt.
   - Every result must show `assessment_year`, `as_of_date`, and official source.

4. **Proof of Submission of Return navigation**
   - Explain whether the user’s described service/activity may require proof, using the current provision and official guidance.

5. **Rate/bracket lookup**
   - Display a stored schedule tied to taxpayer class and assessment year.
   - Do not blend rates from different years.

6. **Small deterministic examples**
   - Allowed only when all inputs and the controlling rate table are explicit.
   - Label the example illustrative, not a filed tax computation.

### Hard abstentions

- Personalized tax minimization.
- Final business liability.
- Foreign income/non-resident complexity.
- VAT, customs, transfer pricing, audits, disputes, and penalties requiring professional analysis.
- Any calculation using a rate not verified for the requested assessment year.

### Mandatory citizen answer format

```text
Your situation
Applicable verified rule
What this means in general
What to do next
Documents/information to prepare
Official sources
What Justor could not verify
As of date + experimental/not-legal-advice label
```

Citizen Mode must not automatically retrieve case law.

---

## 4. Citizen experience: guided first, chat second

Open-ended chat alone will not make the narrow scope reliable. The Citizen Mode landing screen should offer two cards:

```text
Property help | Income-tax help
```

### Property intake

- What are you trying to do: buy, sell, gift, register, check records, rent/lease, resolve co-sharer issue?
- Agricultural or non-agricultural land?
- Your role: owner, buyer, seller, co-sharer, tenant, heir, unsure?
- Is there a written/registered document?
- Relevant date(s)?
- District/area, only where legally material.

### Tax intake

- Assessment year.
- Individual/business/other taxpayer.
- Resident/non-resident/unsure.
- TIN status.
- Broad income categories.
- Vehicle/property/company-director/public-service indicators where the current source makes them material.
- What help is needed: filing requirement, deadline, documents, e-return, PSR, rate lookup?

### Backend decision states

```text
ANSWER | ASK_CLARIFICATION | ABSTAIN | PROFESSIONAL_REFERRAL
```

Clarification should occur only when the missing fact changes the legal route. Abstention must be evidence-driven; do not tune toward a predetermined percentage.

---

## 5. Two-Supabase architecture

Supabase currently allows two active Free Plan projects. Each Free project has a 500 MB database quota and can enter read-only mode above it. The two projects may be under one account/organization; a second account is not required. Keep at least 50 MB operational headroom in each project.

## 5.1 Project A — `justor-core-laws`

Keep:

- Supabase Auth.
- Users/profiles.
- Chats/messages.
- Existing law corpus.
- Pilot-approved provision registry.
- Law versions/amendment events.
- Query runs, claim records, and feedback.

### Minimum additive tables

```text
pilot_provision_registry
law_section_versions
legal_mutation_events
query_runs
answer_claims
feedback_events
pilot_participants
```

### Sidecar whitelist instead of risky full-corpus rewrite

Create `pilot_provision_registry` keyed to the existing law chunk ID:

```text
chunk_id
act_id
section_canonical
workflow_tags[]
source_url
source_hash
legal_status
effective_from
effective_to
as_of_date
verification_status
approved_for_citizen
approval_method
notes
```

Citizen retrieval must include:

```text
approved_for_citizen = true
legal_status in (ACTIVE, AMENDED_CURRENT)
effective_from <= as_of_date
effective_to is null or effective_to > as_of_date
```

This allows the broad corpus to remain available for audit without letting it control citizen answers.

## 5.2 Project B — `justor-cases`

No Auth users, chats, feedback, or frontend access.

Minimum tables:

```text
cases
case_documents
case_pages
case_statute_citations
case_audit_findings
case_ingestion_runs
```

Every searchable case passage must retain:

```text
case_id
official document ID
court/division
case number/year
parties
judgment date
uploaded date
page number
exact selected text
official PDF URL
PDF SHA-256
extraction method/quality
review status
embedding model/dimension/version
```

Never write Project B records into `document_chunks` in Project A.

## 5.3 Embedding contract

The live database, committed schema, and runtime disagree. Do not choose a model from documentation alone.

Run on Project A before changing retrieval:

```sql
select vector_dims(embedding) as dimensions, count(*) as rows
from document_chunks
where embedding is not null
group by vector_dims(embedding);
```

Then:

- If Project A is 768-dimensional, use the exact 768-dimensional law query model used for those records and ensure `match_acts_v2` accepts `vector(768)`.
- If Project A is 1024-dimensional, ensure the column/RPCs are 1024 and use the matching 1024-dimensional law query model.
- If the production model that created the vectors cannot be identified, do not mix new vectors into that index; use exact/lexical retrieval for the citizen whitelist and schedule controlled re-embedding later.

Project B may independently use BGE-M3/1024. In Lawyer Mode, generate the Project B query embedding only when case retrieval is requested. The backend merges text evidence after the two searches; vector dimensions do not need to match across projects.

### Required environment variables

```text
LAWS_SUPABASE_URL
LAWS_SUPABASE_SERVICE_ROLE_KEY
CASES_SUPABASE_URL
CASES_SUPABASE_SERVICE_ROLE_KEY
LAW_EMBEDDING_MODEL
LAW_EMBEDDING_DIM
CASE_EMBEDDING_MODEL=baai/bge-m3
CASE_EMBEDDING_DIM=1024
ALLOWED_ORIGINS
```

Only the public Project A URL and anonymous key may use `VITE_` names in the frontend. Service-role and model keys remain backend-only.

---

## 6. Retrieval and evidence contract

## 6.1 Exact law lookup

Normalize aliases to immutable `act_id`. Normalize a requested provision to `section_canonical`.

```text
TPA + 54A -> act_id=tpa_1882, section_canonical=54A
190(1)(b) -> exact=190(1)(b), explicit parent=190
```

Rules:

- Exact equality first.
- Parent fallback only when the subsection is not separately stored.
- Tell the user when a parent section was used.
- Never use `%section%`, `startswith`, or substring matching for an exact section.
- An exact-section failure causes clarification/abstention, not semantic fallback for a high-risk answer.

## 6.2 Current-law gate

Apply before generation and again before rendering:

```text
current/effective on requested date
approved for requested persona/workflow
correct Act/domain
official source retained
no unresolved critical/high audit finding
```

If all results are filtered, return empty. Never restore the unsafe result set.

Neighbor chunks must pass the same Act, status, version, and pilot-scope filters as the original hit.

## 6.3 Case retrieval gate

Retrieve Project B only when:

- persona is Legal Professional and the user requests case research; or
- question intent is judgment, precedent, judicial interpretation, case brief, parties, case number, or citation.

Student Mode may retrieve cases only in an explicitly labeled case-research workflow. Citizen Mode receives no automatic cases.

## 6.4 Structured answer and citations

The model should return structured claims, not free-form invented tags:

```json
{
  "decision": "answer",
  "summary": "...",
  "claims": [
    {"text": "Atomic legal proposition", "source_ids": ["LAW:<record-id>"]}
  ],
  "next_steps": [],
  "limitations": []
}
```

The backend:

1. Supplies immutable source IDs.
2. Rejects IDs not in the retrieval set.
3. Checks exact Act/section/status/date identity.
4. Runs claim-to-passage support review.
5. Regenerates once on failure.
6. Abstains after the second failure.
7. Renders display tags and source cards itself.

Never silently replace a tag. Never remove a tag while leaving its unsupported claim.

---

## 7. Lawyer Mode and case-law plan

## 7.1 Five-day case target

Select 25–50 official documents, prioritizing:

1. SCOB cases.
2. Appellate Division judgments.
3. Recent/high-use High Court Division judgments relevant to property/tax and pilot lawyers.

For every selected document:

- preserve official PDF and URL;
- hash the PDF;
- store all usable pages, not only the first 10;
- flag OCR pages;
- preserve exact page text;
- store metadata and extraction quality;
- expose page excerpts with visible `AUTO_EXTRACTED` or `SOURCE_VERIFIED` labels.

Do not present AI-generated ratio, holding, treatment, or subsequent history as verified. For the pilot, lawyer results should be extractive:

```text
Case metadata
Relevant page excerpt
Page number
Official PDF
Extraction/review status
Subsequent history not checked
```

## 7.2 Lawyer web workflow

- Search statutes.
- Search official cases.
- Filter by court/division, case number/year, Act, section, and date.
- Open exact page passage and official PDF.
- Copy a citation only when the report/citation field exists in the source.
- Flag wrong extraction, wrong relevance, or missing authority.

Twenty lawyers should test this web workflow first.

## 7.3 Private MCP prototype

Build only three read-only tools in five days:

```text
get_law_section
search_laws
search_cases
```

`search_cases` returns page passages and official URLs. The MCP imports the same retrieval/evidence service used by the web API. It must not contain duplicate retrieval logic.

Use local/private `stdio` for Mehedi and a few technical testers. Do not publish an unauthenticated remote MCP. Ordinary lawyers do not need MCP installation for the first pilot.

---

## 8. Security and privacy gates

Before any external tester:

1. Validate the Project A Supabase JWT on `/chat`, `/upload`, `/upload/status`, `/documents`, delete routes, feedback, and analytics.
2. Derive `user_id` from the validated token; ignore caller-supplied IDs.
3. Apply explicit CORS origins from `ALLOWED_ORIGINS`.
4. Add per-user/IP rate limits.
5. Sanitize rendered Markdown with DOMPurify at every model-output insertion.
6. Send the `Authorization: Bearer <token>` header from the frontend.
7. Test RLS for chats/messages/feedback/documents.
8. Disable upload/document-analysis UI and endpoints for external testers unless isolation passes.
9. Remove provider keys and unsafe instructions from README and deployment files.
10. Rotate any Groq/Dify key ever deployed with a `VITE_` prefix.
11. Redact or avoid storing sensitive names, NID/TIN numbers, addresses, and document contents in telemetry.
12. Obtain consent for storing pilot questions and quotations.

The current destructive `backend/supabase_schema.sql` must never be run on production. Create additive timestamped migrations and take verified exports first.

---

## 9. Telemetry for product improvement and iDEA evidence

Every request receives a backend-generated `query_run_id`.

### `query_runs`

```text
query_run_id
created_at
pseudonymous_user_id
persona
workflow
consent_status
redacted_query
classification
requested_as_of_date/assessment_year
retrieval_plan
law_source_ids
case_source_ids
decision
abstention_reason
model/prompt/embedding versions
latency_ms
error_code
```

### `answer_claims`

```text
query_run_id
claim_index
claim_text_or_hash
source_ids
support_status
validator_version
```

### `feedback_events`

```text
query_run_id
rating
reason_code
comment
source_opened
created_at
```

Reason codes:

```text
HELPFUL
WRONG_LAW
WRONG_SECTION
OUTDATED
UNSUPPORTED
TOO_VAGUE
TOO_COMPLEX
MISSING_CASE
BAD_CASE_MATCH
TECHNICAL_ERROR
```

### Honest pilot metrics

- invited, activated, and returning users;
- queries per persona/workflow;
- correct routing/source retrieval on frozen tests;
- source-card open rate;
- helpful/not-helpful feedback;
- wrong-law/wrong-section/outdated flags;
- clarification and abstention reasons;
- latency and technical failure rate;
- case-result open rate;
- issues fixed from observed feedback.

Do not label product analytics as “legal accuracy.”

---

## 10. Five-day execution schedule

## Day 1 — Freeze, back up, align, and secure

### Mehedi

- Create a pilot branch and tag the current commit.
- Export Project A schema/data and record table/index sizes.
- Run vector-dimension and Act/chunk inventory SQL.
- Choose the law embedding contract based on live data.
- Split `laws_db` and `cases_db` configuration.
- Fix CORS and backend JWT authentication.
- Derive user identity from JWT.
- Add DOMPurify and remove unsafe README secrets.
- Disable destructive schema execution and corrupt case promotion.

### Taj + AI

- Freeze the exact citizen workflows and hard abstentions.
- Choose the pilot Acts/instruments and 25–50 case documents.
- Create the source-verification worksheet.
- Freeze a 50-question test set.
- Draft consent, disclaimer, and closed-pilot wording.

### Day 1 gate

- Verified backup exists.
- Project A dimension/model decision recorded.
- No browser model/service-role secret.
- Protected endpoints reject missing/invalid JWTs.
- Frontend renders sanitized model Markdown.

## Day 2 — Citizen evidence layer and Project B

### Mehedi

- Create additive Project A pilot tables.
- Create Project B case tables/indexes.
- Add Project B-only environment variables to the Supreme Court pipeline.
- Build exact Act/section canonical lookup.
- Add the current-law and pilot-whitelist gates.
- Remove unsafe fallback and re-filter neighbors.
- Gate case retrieval by persona/intent.

### Taj + AI

- Source-check and approve the first 50–100 high-use property/tax provisions.
- Record official URLs, hashes, status, date, workflow tags, and limitations.
- Reject or quarantine conflicting/unverifiable rows.

### Day 2 gate

- Citizen queries can retrieve only approved provisions.
- Section 4 cannot match 14/40/54.
- Dead/unapproved law returns clarification or abstention.
- Citizen queries make zero Project B searches.

## Day 3 — Case search and guided Citizen Mode

### Mehedi

- Ingest 25–50 selected official judgments/SCOB documents into Project B.
- Preserve all usable pages and official URLs/hashes.
- Add exact/lexical filters and semantic case search.
- Build lawyer case result cards.
- Add citizen property/tax intake and clarification state.
- Return structured answer/claim/source objects.

### Taj + AI

- Inspect a sample of five cases page-by-page.
- Verify metadata and page citations for priority results.
- Test citizen follow-ups and wording in Bangla and English.

### Day 3 gate

- Every case result opens the official PDF and exact page reference.
- No case is represented as an Act.
- No generated ratio/holding is labeled verified.
- Property/tax workflows ask required material facts.

## Day 4 — Citation enforcement, telemetry, feedback, and MCP

### Mehedi

- Replace the current citation verifier with claim/source validation.
- Regenerate once, then abstain.
- Add `query_run_id`, answer claims, and feedback endpoint.
- Link frontend feedback to the displayed answer’s `query_run_id`.
- Build the three private read-only MCP tools.
- Run RLS and cross-user tests.

### Taj + AI

- Run supported, restricted, adversarial, historical, and cross-jurisdiction tests.
- Review every failed claim/citation pair.
- Prepare the announcement, onboarding form, tester guide, and grant evidence folder.

### Day 4 gate

- Zero invented source IDs.
- Citation failure never leaves unsupported prose visible.
- Every response and feedback event has a `query_run_id`.
- User A cannot read or mutate User B’s records.
- All three MCP tools work locally and are read-only.

## Day 5 — Regression, load, smoke pilot, deploy, announce

### Mehedi

- Run clean install/build, Python tests, migrations, and deployment smoke tests.
- Run frozen 50-question regression.
- Run a 200-query low-concurrency load/reliability test.
- Inspect error/latency/log correlation.
- Deploy the closed pilot and verify source links.

### Taj

- Onboard 2 lawyers, 3 students, and 5 citizens first.
- Observe their first sessions.
- Fix any critical issue before sending the wider invitation.
- Publish the closed-pilot recruitment/invitation announcement.
- Start the iDEA application pack with screenshots and first observed data.

### Day 5 gate

- Zero cross-user leakage.
- Zero fabricated IDs/citations in the frozen set.
- 100% correct abstention on frozen prohibited questions.
- At least 90% correct route and exact-source retrieval on supported frozen questions.
- Under 2% technical failures in the reliability test.
- 100% of displayed feedback linked to the correct run.
- No repealed/omitted law presented as current in the frozen test.

If a gate fails, announce recruitment but delay account access until it passes.

---

## 11. Frozen test composition

Use 50 questions:

| Category | Count |
|---|---:|
| Supported property workflows | 12 |
| Supported tax workflows | 10 |
| Exact section/current-versus-historical | 8 |
| Lawyer case search/page citation | 8 |
| Deliberately unsupported/high risk | 8 |
| Adversarial Indian-law/citation injection | 4 |

Each gold record must include:

```text
expected route
required clarification facts
allowed source IDs
prohibited source IDs
expected decision
required warnings
review notes
```

Measure routing, source retrieval, current/historical status, citation mapping, abstention, and technical reliability separately.

---

## 12. Pilot rollout after Day 5

| Wave | Lawyers | Students | Citizens | Cumulative | Condition |
|---|---:|---:|---:|---:|---|
| Day 5 smoke | 2 | 3 | 5 | 10 | All launch gates pass |
| Days 6–8 | 5 | 10 | 25 | 40 | No critical safety/privacy defect for 48 hours |
| Week 2 | 10 | 25 | 60 | 95 | Wrong/unsupported flags under 10%; failures under 2% |
| Week 3 | 20 | 40 | 100 | 160 | Stable metrics and no citation/current-law regression |

Pause expansion immediately for:

- cross-user data exposure;
- fabricated source/citation;
- dead law presented as current;
- repeated wrong-law routing;
- missing run IDs;
- unexpected cost/quota exhaustion;
- more than 10% wrong/unsupported feedback in a workflow.

---

## 13. Closed-pilot announcement wording

> **Justor AI Closed Pilot — Applications Open**  
> We are inviting a small group of Bangladeshi lawyers, law students, and citizens to test Justor AI’s source-linked legal information experience. The first citizen workflows focus on property and income-tax navigation. Lawyer Mode adds statute research and page-linked official judgment search. Justor is experimental, AI source-checked, and not yet lawyer-verified; it will ask for clarification or decline when it cannot support an answer from its approved sources. Pilot feedback will directly guide the next build.

Do not use:

- “AI lawyer”;
- “A–Z Bangladesh law”;
- “zero hallucination”;
- “80% legally accurate”;
- “fully verified Bangladesh law database.”

---

## 14. iDEA grant evidence pack

The official iDEA application portal currently offers a Startup Grant application and Startup Grant documentation. Prepare:

1. Ten-slide pitch deck.
2. A 60–90 second product demo.
3. Pilot charter and narrow safety scope.
4. Architecture diagram and two-project data plan.
5. Screenshots of source cards, clarification, abstention, and lawyer case results.
6. Activated/returning-user and workflow metrics.
7. Consent-approved feedback quotations.
8. Three short observed user stories: lawyer, student, citizen.
9. Product risk register and mitigation evidence.
10. Twelve-month budget showing how the grant funds legal review, data engineering, security, infrastructure, and pilots.
11. Roadmap from Bangladesh proof market to portable jurisdiction/legal-intelligence infrastructure.

Apply as soon as the portal requirements are satisfied and the pilot has honest early evidence. Do not wait for 160 completed users if the application is ready; update the evidence during evaluation.

Official portal: `https://apply.idea.gov.bd/`

---

## 15. What not to do in these five days

- Do not ingest the entire 2,388-file law corpus again.
- Do not ingest 250+ cases before the 25–50-document gates pass.
- Do not delete Project A case rows immediately after copying; verify counts/hashes and switch traffic first.
- Do not run the current destructive schema file.
- Do not re-embed the full law database unless the live embedding audit proves it is necessary and feasible.
- Do not build five MCP tools or a public remote MCP.
- Do not enable sensitive document uploads for external testers without RLS/isolation tests.
- Do not auto-apply amendments or overwrite current law from a live page.
- Do not treat an official PDF as proof that AI-extracted ratio/holding is correct.
- Do not tune abstention to a cosmetic percentage.
- Do not publish an accuracy percentage from the existing checker.

---

## 16. The first two hours

Mehedi should do these in order:

1. Create a pilot branch and tag commit `83638f2`.
2. Export Project A and capture table/index sizes.
3. Run vector dimension, Act inventory, status distribution, and database-size SQL.
4. Disable the corrupt case promotion command and mark the destructive schema file `DO_NOT_RUN_PRODUCTION`.
5. Add separate Project A/Project B environment-variable names.
6. Decide the Project A embedding contract from live evidence.
7. Start JWT/CORS/DOMPurify fixes.

Taj should simultaneously:

1. Choose the first 2 lawyers, 3 students, and 5 citizens.
2. Freeze the six property and six tax workflows.
3. Select the priority Acts/instruments and 25–50 official case documents.
4. Approve the closed-pilot disclaimer and consent wording.
5. Create the iDEA evidence checklist.

AI support should simultaneously prepare:

1. Additive SQL migrations.
2. Exact Act/section canonicalization tests.
3. The 50-question frozen evaluation set.
4. Source-verification worksheets.
5. Adversarial citation/current-law tests.
6. Announcement/onboarding copy and grant evidence templates.

---

## 17. Final success definition

At the end of five days, success is not “Justor knows every law.”

Success is:

> A closed pilot can safely answer a narrow set of property and tax navigation questions from approved current sources, ask the right follow-up, abstain outside scope, let lawyers search official case passages with page links, preserve user isolation, and record every answer/feedback event as evidence for product improvement and grant evaluation.

That is both achievable and strategically strong.

---

## 18. Current official references checked

- iDEA Startup Grant application portal: `https://apply.idea.gov.bd/`
- Supabase Free Plan/billing: `https://supabase.com/docs/guides/platform/billing-on-supabase`
- Supabase database/read-only behavior: `https://supabase.com/docs/guides/platform/database-size`
- Bangladesh Code Transfer of Property Act Section 54A: `https://bdlaws.minlaw.gov.bd/act-48/section-16095.html`
- NBR Income Tax Act, 2023 official English text: `https://nbr.gov.bd/uploads/acts/Income_tax_act_2023.pdf`
- NBR current income-tax notices: `https://nbr.gov.bd/information-library/publicnotice-details/income-tax/eng`
- NBR income-tax SROs: `https://nbr.gov.bd/regulations/sros/income-tax-sros/eng`

