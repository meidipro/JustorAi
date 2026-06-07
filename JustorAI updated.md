# Justor AI — MASTER Deploy File (single source of truth)

This supersedes `JustorAI_Pilot_Deploy_Pack.md` and the prompt-library file as the **one** file to deploy from. It is written against your real code (`_embed`, `retrieve_context(query_vec, intent)`, provider strings `alibaba`/`gemini`/`groq`, `match_dlrs_v2` 3-param). Work top to bottom.

**What this delivers:** stronger retrieval (act-aware, scoring fixed), refuse-on-uncertainty, citation integrity, fallback-model safety, and full query logging. **What it does not deliver by itself:** a proven accuracy number. That comes from STEP 6 (deploy + re-grade). Treat any % as unproven until measured.

---

## 0. What changed vs your current code (the diffs, in one place)

| Area | Change | Why |
|---|---|---|
| `match_acts_v2` SQL | Active & Amended both `+0.20` (was 0.22/0.16); dead-law `-0.25`; new `filter_act_name` soft boost `+0.30`; threshold `0.40` | Stop amended core sections (e.g. NAT §7) being out-ranked by less-relevant active ones; bias toward the named act |
| `classify_query` | Detect Act name → `detected_act` | Enables act-aware retrieval |
| `retrieve_context` | Over-fetch 8, then Python post-filter to the named act *only when a match exists* | Kills cross-act answers without the empty-result landmine a hard SQL filter creates |
| `validate_retrieval` | NEW — refuse when named act/section is absent | A clean "not in my database" beats a confident wrong answer |
| `format_retrieved_context` | Returns `(context, sources)`; cleans verbose Act_Name; flags status | Better citations; no "(East Bengal Act)( ACT NO...)" leaking into answers |
| `build_citation_footer` | NEW — clean Sources block for Public/Student | Citation consistency |
| `call_llm_with_fallbacks` | Returns `(text, model_id)`; compresses prompt for 8B; lawyer chain ends at 70B | Know which model answered; stop 8B from doing IRAC |
| `/chat` | Returns `sources`, `model_used`, `retrieval_status`; logs every query | Pilot analytics + fundraise data |
| `pilot_query_log` | NEW table | The data you show investors |

`match_dlrs_v2` is **unchanged** — do not touch it.

---

## STEP 0 — Confirm the database (5 min, do before anything else)

Your own technical notes warn that `ingest_json.py` / `ingest_dlr.py` may use the **old embedder** while `ingest_v2.py` uses Gemini 768-dim. If any chunk was embedded at the wrong dimension, similarity is garbage and no code below helps.

```sql
-- 0a. Embedding dimension sanity — every row must be 768
SELECT vector_dims(embedding) AS dims, count(*) AS rows
FROM document_chunks
GROUP BY vector_dims(embedding);

-- 0b. Which acts are actually ingested (this list = your pilot scope)
SELECT act_name, count(*) AS chunks
FROM document_chunks
WHERE document_type = 'Act'
GROUP BY act_name
ORDER BY act_name;

-- 0c. DLR present?
SELECT count(*) FROM document_chunks WHERE document_type = 'DLR';
```

**Gate:** if 0a shows any non-768 rows → re-ingest them with `_embed`/`ingest_v2.py` first. If acts are missing → they are not in pilot scope; do not list them to users.

---

## STEP 1 — SQL (Supabase SQL editor)

### 1.1 Replace `match_acts_v2`

```sql
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
```

### 1.2 Pilot logging table

```sql
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
create index if not exists pilot_log_created_idx on pilot_query_log (created_at desc);
create index if not exists pilot_log_status_idx  on pilot_query_log (retrieval_status);
alter table pilot_query_log enable row level security;
create policy "service_role_full_access" on pilot_query_log for all using (true);
```

Verify: `\df match_acts_v2` and `\d pilot_query_log`.

---

## STEP 2 — backend.py (paste in this order)

> Uses your existing globals: `supabase`, `Client`, `cast`, `_embed`, `logger`, `dashscope_client`, `gemini`/`GEMINI_API_KEY` via `_call_gemini_native`, `groq_client`, `openrouter_client`, `HTTPException`, `JSONResponse`, `re`. Keep your existing `prompt_lawyer` / `prompt_law_student` / `prompt_general_public` exactly as they are — STEP 3 adds two lines to them.

### 2.1 ACT_NAME_MAP + classify_query (replace existing)

```python
import re

# Add a line ONLY for acts confirmed present in STEP 0b.
ACT_NAME_MAP = {
    r'nat act|non.?agricultural tenancy act': 'The Non-Agricultural Tenancy Act, 1949',
    r'land reforms act|bhumi sanskar|land reform 2023': 'The Land Reforms Act, 2023',
    r'\bsat act\b|state acquisition.*tenancy|sat 1950': 'The State Acquisition and Tenancy Act, 1950',
    r'transfer of property act|\btpa\b': 'The Transfer of Property Act, 1882',
    r'trademarks? act|trademark 2009': 'The Trademarks Act, 2009',
    # r'penal code': 'The Penal Code, 1860',
    # r'\bcrpc\b|criminal procedure': 'Code of Criminal Procedure, 1898',
    # r'\bcpc\b|civil procedure': 'Code of Civil Procedure, 1908',
    # r'evidence act': 'The Evidence Act, 1872',
    # r'contract act': 'The Contract Act, 1872',
    # r'limitation act': 'The Limitation Act, 1908',
    # r'specific relief': 'The Specific Relief Act, 1877',
    # r'registration act': 'The Registration Act, 1908',
    # r'partition act': 'The Partition Act, 1893',
    # r'mflo|muslim family': 'Muslim Family Laws Ordinance, 1961',
}

def classify_query(query: str) -> dict:
    section_pattern = (
        r"(?:section|sec\.?|dhara|\u09a7\u09be\u09b0\u09be|article|\u0985\u09a8\u09c1\u099a\u09cd\u099b\u09c7\u09a6|rule)"
        r"\s*(\d+[A-Za-z]?)"
    )
    sections = re.findall(section_pattern, query, re.IGNORECASE)

    detected_act = None
    for pattern, act_name in ACT_NAME_MAP.items():
        if re.search(pattern, query, re.IGNORECASE):
            detected_act = act_name
            break

    return {
        "is_dlr_request": any(k in query.lower() for k in
            ["dlr", "case law", "judgment", "\u09a8\u099c\u09c0\u09b0", "precedent", "court held"]),
        "is_repealed_request": any(k in query.lower() for k in
            ["repealed", "\u09ac\u09be\u09a4\u09bf\u09b2", "omitted", "old law", "previously", "was it ever"]),
        "sections": sections,
        "primary_section": sections[0] if sections else None,
        "detected_act": detected_act,
    }
```

### 2.2 Act-match helper + retrieve_context (replace existing)

```python
def _act_matches(chunk_act: str, detected: str) -> bool:
    a, b = (chunk_act or "").lower(), (detected or "").lower()
    return bool(a) and bool(b) and (a in b or b in a)

async def retrieve_context(query_vec: list, intent: dict):
    db = cast(Client, supabase)

    acts_search = db.rpc("match_acts_v2", {
        "query_embedding": query_vec,
        "match_count": 8,                       # over-fetch; trimmed below
        "match_threshold": 0.40,
        "query_section": intent.get("primary_section"),
        "prefer_dead_law": intent.get("is_repealed_request", False),
        "prefer_amended": False,
        "filter_act_name": intent.get("detected_act"),
    }).execute()
    acts = acts_search.data or []

    # Cross-act post-filter: if a specific act was named AND we found chunks
    # from it, keep ONLY those. If none matched, leave as-is (validate_retrieval
    # will refuse, which is correct). This avoids false refusals on misdetection.
    detected = intent.get("detected_act")
    if detected:
        same = [a for a in acts if _act_matches(a.get("act_name", ""), detected)]
        acts = (same or acts)[:6]
    else:
        acts = acts[:6]

    dlrs_search = db.rpc("match_dlrs_v2", {
        "query_embedding": query_vec,
        "match_count": 2,
        "match_threshold": 0.40,
    }).execute()

    return acts, dlrs_search.data or []
```

### 2.3 validate_retrieval (new)

```python
def validate_retrieval(intent: dict, acts: list, dlrs: list):
    """Returns (is_valid, status_code)."""
    if not acts and not dlrs:
        return False, "no_results"
    if intent.get("detected_act") and acts:
        if not any(_act_matches(a.get("act_name", ""), intent["detected_act"]) for a in acts):
            return False, "wrong_act_retrieved"
    if intent.get("primary_section") and acts:
        secs = [str(a.get("section_number", "")).lower() for a in acts]
        if str(intent["primary_section"]).lower() not in secs:
            return True, "section_not_exact"   # soft: section may be inside related chunk
    return True, "ok"
```

### 2.4 clean_act_name + format_retrieved_context (replace existing)

```python
def clean_act_name(raw: str) -> str:
    cleaned = re.sub(r'\s*\([^)]*\)', '', raw or '').strip().rstrip('.,;:').strip()
    return cleaned or (raw or 'Unknown Act')

def format_retrieved_context(acts: list, dlrs: list):
    """Returns (context_block, sources_list)."""
    if not acts and not dlrs:
        return "NO_VERIFIED_SOURCES_FOUND", []

    sources = []
    block = "=== STATUTORY LAW (ACTS) ===\n"
    if not acts:
        block += "No matching Acts found for this query.\n"
    for i, act in enumerate(acts):
        sid = f"ACT-{i+1}"
        name = clean_act_name(act.get('act_name', ''))
        num, title = act.get('section_number', ''), act.get('section_title', '')
        status = act.get('status') or 'Active'
        sl = status.lower()
        if sl == 'omitted':
            tag = " \u26a0\ufe0f [STATUS: OMITTED \u2014 NO LONGER EXISTS IN BANGLADESH LAW]"
        elif sl == 'repealed':
            tag = " \u26a0\ufe0f [STATUS: REPEALED \u2014 NO LONGER IN FORCE]"
        elif sl == 'amended':
            tag = " [STATUS: AMENDED \u2014 current law; see amendment notes]"
        elif sl == 'active':
            tag = ""
        else:
            tag = f" [STATUS: {status.upper()}]"
        block += f"[{sid}] {name} \u2014 Section {num}: {title}{tag}\n"
        block += f"Content: {act.get('content','')}\n"
        if act.get('repealed_clauses'):
            block += f"Omission/Repeal Authority: {act['repealed_clauses']}\n"
        if act.get('amendment_notes'):
            block += f"Amendment Notes: {act['amendment_notes']}\n"
        block += "---\n"
        sources.append({"id": sid, "type": "statute", "act": name,
                        "section": num, "title": title, "status": status})

    block += "\n=== CASE LAW (DLR) ===\n"
    if not dlrs:
        block += "No matching Case Law found for this query.\n"
    for i, dlr in enumerate(dlrs):
        sid = f"DLR-{i+1}"
        title = dlr.get('case_title', 'Unknown Case')
        year, court = dlr.get('year', ''), dlr.get('court_division', '')
        cite = dlr.get('dlr_citation') or \
            f"{dlr.get('dlr_volume','')} DLR ({dlr.get('dlr_series','AD')}) {year}".strip()
        block += (f"[{sid}] Case: {title} ({year})\nCitation: {cite}\nCourt: {court}\n"
                  f"Subject: {dlr.get('subject_law','')}\n"
                  f"Ratio Decidendi: {dlr.get('ratio_decidendi','')}\n"
                  f"Reference Context: {(dlr.get('judgment_content','') or '')[:300]}...\n---\n")
        sources.append({"id": sid, "type": "case_law", "case": title,
                        "court": court, "year": year, "citation": cite})

    return block, sources
```

### 2.5 build_citation_footer (new)

```python
def build_citation_footer(answer: str, sources: list) -> str:
    if "REFERENCES" in answer or not sources:   # lawyer IRAC builds its own
        return answer
    used = {u.strip('[]') for u in re.findall(r'\[(?:ACT|DLR)-\d+\]', answer)}
    cited = [s for s in sources if s['id'] in used] or sources
    lines = ["\n\n---\n**Sources**"]
    for s in cited:
        if s['type'] == 'statute':
            lines.append(f"- **[{s['id']}]** {s['act']}, Section {s['section']}: "
                         f"{s['title']} *(Status: {s['status']})*")
        else:
            lines.append(f"- **[{s['id']}]** {s['case']} \u2014 {s.get('citation','')} "
                         f"| {s.get('court','')} | {s.get('year','')}")
    return answer + "\n".join(lines)
```

### 2.6 Fallback prompt + compression + model chains + call_llm_with_fallbacks (replace existing)

> **Signature changes from `-> str` to `-> (str, str)`. Update any other call site to unpack the tuple.**

```python
SMALL_MODELS = {"llama-3.1-8b-instant"}

FALLBACK_PROMPT = """You are Justor AI, a Bangladesh legal information assistant.
Answer ONLY from VERIFIED SOURCES below. Never use training memory.
Tag every legal claim with its source: [ACT-1], [ACT-2], [DLR-1].
Never write a tag that is not in the sources. Use section numbers exactly as
they appear in the sources, never from the question.
If VERIFIED SOURCES is empty: reply exactly "Not in my verified database.
Please consult the Bangladesh Code or a licensed lawyer." and nothing else.
Never cite Indian law. If a source is Omitted/Repealed, say it is not current law.

VERIFIED SOURCES:
{context}

End with: "\u26a0\ufe0f Verify with a licensed Bangladeshi lawyer before acting."
"""

def _extract_context(messages: list) -> str:
    sys = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
    i = sys.find("VERIFIED SOURCES")
    return sys[i:] if i != -1 else "No verified sources."

def compress_for_small_model(messages: list) -> list:
    ctx = _extract_context(messages)
    return [{"role": "system", "content": FALLBACK_PROMPT.format(context=ctx)}] + messages[1:]

# Provider strings match your code: "alibaba", "gemini", "groq".
# Lawyer chain intentionally ends at the 70B — never route IRAC to the 8B.
MODEL_CHAINS = {
    "Legal Professional": [("alibaba","qwen-max"), ("gemini","gemini-2.5-flash"),
                           ("groq","llama-3.3-70b-versatile")],
    "Law Student":        [("alibaba","qwen-plus"), ("gemini","gemini-2.5-flash"),
                           ("groq","llama-3.3-70b-versatile"), ("groq","llama-3.1-8b-instant")],
    "General Public":     [("gemini","gemini-2.5-flash"), ("alibaba","qwen-plus"),
                           ("groq","llama-3.3-70b-versatile"), ("groq","llama-3.1-8b-instant")],
}

def call_llm_with_fallbacks(models: list, messages) -> tuple:
    """Returns (text, 'provider/model'). Compresses the prompt for small models."""
    for provider, model in models:
        try:
            payload = compress_for_small_model(messages) if model in SMALL_MODELS else messages
            if provider == "alibaba" and dashscope_client:
                c = dashscope_client.chat.completions.create(
                    model=model, messages=payload, temperature=0.1, max_tokens=2000)
                return c.choices[0].message.content, f"{provider}/{model}"
            elif provider == "gemini" and GEMINI_API_KEY:
                return _call_gemini_native(payload, temperature=0.1), f"{provider}/{model}"
            elif provider == "groq" and groq_client:
                c = groq_client.chat.completions.create(
                    model=model, messages=payload, temperature=0.1, max_tokens=2000)
                return c.choices[0].message.content, f"{provider}/{model}"
            elif provider == "openrouter" and openrouter_client:
                c = openrouter_client.chat.completions.create(
                    model=model, messages=payload, temperature=0.1, max_tokens=2000)
                return c.choices[0].message.content, f"{provider}/{model}"
        except Exception as e:
            logger.warning(f"[LLM] {provider}/{model} failed: {e}")
            continue
    raise HTTPException(status_code=503, detail="AI service busy. Please try again in a moment.")
```

### 2.7 log_query (new)

```python
def log_query(**row):
    try:
        row["query"] = (row.get("query") or "")[:500]
        row["response_preview"] = (row.get("response_preview") or "")[:300]
        cast(Client, supabase).table("pilot_query_log").insert(row).execute()
    except Exception as e:
        logger.warning(f"pilot log failed (non-critical): {e}")
```

### 2.8 get_system_prompt (replace existing)

```python
def get_system_prompt(role: str, context: str) -> str:
    if context == "NO_VERIFIED_SOURCES_FOUND":
        return ("You are Justor AI. The verified database returned no results. "
                "Reply with EXACTLY: \"I don't have verified information on this "
                "in my database yet. Please consult the Bangladesh Code at "
                "bdlaws.minlaw.gov.bd or a licensed lawyer.\" Do not use training memory.")
    if role == "Legal Professional": return prompt_lawyer(context)
    if role == "Law Student":        return prompt_law_student(context)
    return prompt_general_public(context)
```

### 2.9 /chat endpoint (replace existing)

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    intent = classify_query(request.message)
    query_vec = _embed(request.message)                 # your existing embedder
    acts, dlrs = await retrieve_context(query_vec, intent)
    ok, status = validate_retrieval(intent, acts, dlrs)

    if not ok:
        msg = {
            "no_results": ("I don't have verified information on this specific topic "
                           "in my database yet. Please consult the Bangladesh Code at "
                           "bdlaws.minlaw.gov.bd or call Legal Aid at 16430."),
            "wrong_act_retrieved": ("I could not locate the specific Act you asked about "
                           "in my verified database. Please consult the Bangladesh Code "
                           "or a licensed lawyer for this question."),
        }.get(status, "Not found in verified database.")
        log_query(user_id=request.user_id, persona=request.role, query=request.message,
                  act_detected=intent.get("detected_act"),
                  section_detected=intent.get("primary_section"),
                  sources_found=0, retrieval_status=status,
                  model_used="none-refused", response_preview=msg)
        return JSONResponse(content={
            "response": msg, "sources_used": 0, "sources": [], "retrieval_status": status,
            "metadata": {"detected_act": intent.get("detected_act"),
                         "sections_found": intent["sections"]}})

    context, sources = format_retrieved_context(acts, dlrs)
    messages = [{"role": "system", "content": get_system_prompt(request.role, context)}]
    messages += [{"role": m.role, "content": m.content} for m in (request.history or [])[-6:]]
    messages.append({"role": "user", "content": request.message})

    models = MODEL_CHAINS.get(request.role, MODEL_CHAINS["General Public"])
    answer, model_used = call_llm_with_fallbacks(models, messages)
    final = answer if request.role == "Legal Professional" else build_citation_footer(answer, sources)

    log_query(user_id=request.user_id, persona=request.role, query=request.message,
              act_detected=intent.get("detected_act"),
              section_detected=intent.get("primary_section"),
              sources_found=len(acts) + len(dlrs), retrieval_status=status,
              model_used=model_used, response_preview=final)

    return JSONResponse(content={
        "response": final, "sources_used": len(acts) + len(dlrs), "sources": sources,
        "retrieval_status": status, "model_used": model_used,
        "metadata": {"detected_act": intent.get("detected_act"),
                     "sections_found": intent["sections"],
                     "section_detected": intent.get("primary_section"),
                     "is_dlr": intent["is_dlr_request"]}})
```

---

## STEP 3 — Two edits to your existing persona prompts

Do **not** rewrite the prompts (your 10 zero-hallucination rules are good and re-typing them risks corrupting tuned safety text). Insert two things:

**3.1 — All three prompts (`prompt_lawyer`, `prompt_law_student`, `prompt_general_public`), add to the rules block:**
```
CITATION INTEGRITY: Never write an [ACT-N] or [DLR-N] tag that does not appear
in VERIFIED SOURCES above. State every section number exactly as it appears in
VERIFIED SOURCES — never copy a section number from the user's question.
```

**3.2 — `prompt_lawyer` only, inside the APPLICATION section instruction:**
```
STRICT APPLICATION RULE: Reason ONLY from rules quoted in RULE above. Do not
introduce any doctrine, principle, or statutory language not quoted there —
even from the same Act, even if you believe it applies. If you reach for
anything not in RULE, stop and write: "[X] may be relevant but is not in my
verified sources; independent verification required." Do not mix language from
different sections unless both are quoted in RULE.
```
This is the fix for the Q19/Q20 failures (Section 41 language bleeding into a Section 52 analysis; the "void ab initio" insertion).

---

## STEP 4 — Deploy

1. Run STEP 1 SQL; verify functions/table exist.
2. Paste STEP 2 (2.1 → 2.9). Search the repo for other callers of `call_llm_with_fallbacks` and `format_retrieved_context` and update them to the new return shapes.
3. Apply STEP 3 edits.
4. Push → Render auto-deploys → hit `/health`.

---

## STEP 5 — Smoke test (sanity checks, NOT your eval set)

Run live; check the JSON `model_used` and `retrieval_status` fields and the `pilot_query_log` rows.

```
1. "Section 7 NAT Act — tenant holding after lease expiry"  [Law Student]        -> §7; model_used != 8B
2. "Inherited 70 bighas under Land Reforms Act 2023"         [General Public]     -> §4(5), compensation
3. "Section 26A NAT Act sub-letting"                         [Legal Professional] -> §26A IRAC, clean Act name in refs
4. "Section 438 anticipatory bail"                           [Legal Professional] -> refusal / omitted (not in scope)
5. "Penal Code Section 302"                                  [General Public]     -> clean refusal IF Penal Code not ingested
```
Checks 4–5 returning **refusals** is the win, not a bug.

---

## STEP 6 — Measure (the real gate; nothing above proves accuracy)

1. **Re-grade the existing 20 with a correct key, ideally a second lawyer.** Q6 was mis-graded (LRA §4(5): inherited excess land *does* get compensation). Until the key is right, the 38% is unreliable both ways.
2. **Write 40–60 fresh questions across only your ingested acts (STEP 0b list). Lock them away.** The original 20 are burned — re-running them measures memorization, not accuracy. Your quotable number comes from the fresh set.
3. **Read `pilot_query_log.model_used` after the run.** Any lawyer answer from the 8B is an infra issue, not a data issue (and STEP 2.6 should have stopped it).

Target framing for the raise: *"measured accuracy X% on N validated acts + refuse-on-uncertainty + here is the per-act expansion pipeline"* — not an act count.

---

## Appendix — integration gotchas

- **Provider strings** must be `alibaba` / `gemini` / `groq` (matches your `call_llm_with_fallbacks`). Wrong strings = every model skipped = 503.
- **`call_llm_with_fallbacks` now returns a tuple.** Unpack everywhere it's called.
- **`format_retrieved_context` now returns a tuple.** Same.
- **Ingestion embedder:** confirm `ingest_json.py` / `ingest_dlr.py` use the 768-dim Gemini path (your notes flag they may not). Mixed dimensions silently break search.
- **Deduplicate the source list** before ingesting more acts (Labour Act listed twice; "Income tax act 2023" likely == "Tax law 2023"). Duplicate acts make near-identical chunks compete and cause wrong-citation behavior.
- **Per-act lawyer sign-off** (gate in the prompt-library file) before any act enters live pilot scope. No code replaces this.
