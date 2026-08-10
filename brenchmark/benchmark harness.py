#!/usr/bin/env python3
"""
Justor AI — Benchmark Harness
==============================

Runs justor_benchmark_verified_45.csv against the live /chat endpoint,
applies deterministic legal-safety checks (these do NOT depend on any
LLM judge), and — if the backend returns retrieved context — scores
RAGAS metrics (Faithfulness, Answer Relevancy, Context Precision,
Context Recall).

WHY DETERMINISTIC CHECKS EXIST SEPARATELY FROM RAGAS:
In the 5-row smoke test, gpt-4o-mini gave Faithfulness = 1.0 to two
answers that contained a fabricated case citation and a wrong section
number. The deterministic checks below catch exactly those two failure
types with plain code, no LLM judgment call involved — so do not skip
them even after RAGAS is wired up correctly.

------------------------------------------------------------------
BACKEND CONTRACT THIS SCRIPT NEEDS (give this section to Mehedi)
------------------------------------------------------------------
For the deterministic checks and RAGAS context metrics to work, POST
/chat should accept an optional eval flag and return the chunks it
actually retrieved and used for generation:

  Request:
    {
      "message": "...",
      "user_id": "benchmark-harness",
      "role": "General Public",
      "history": [],
      "eval_mode": true            <- NEW, optional
    }

  Response (when eval_mode=true), in addition to the existing fields:
    {
      "response": "...",
      "sources_used": 4,
      "retrieved_sources": [
        {
          "tag": "ACT-1",                 <- matches [ACT-1]/[DLR-1] style
          "document_type": "Act",          <-   tags the model is asked to cite
          "act_name": "Transfer of Property Act, 1882",
          "section_number": "9",
          "content": "..."
        },
        {
          "tag": "DLR-1",
          "document_type": "DLR",
          "case_title": "Md. Sarafat Ali v Md. Abdul Gafur",
          "citation": "38 DLR (AD) 161",
          "ratio_decidendi": "..."
        }
      ]
    }

If this isn't wired up yet: the script still runs (deterministic checks
fall back to querying document_chunks directly via Supabase — see
SUPABASE_* env vars below), but RAGAS context metrics will be skipped
and marked "NOT_AVAILABLE" in the output, not silently faked as 0 or N/A
mixed in with real scores.

------------------------------------------------------------------
ENV VARS NEEDED
------------------------------------------------------------------
  JUSTOR_BACKEND_URL          e.g. https://justorai-backend.onrender.com
  SUPABASE_URL                 (for deterministic fallback checks)
  SUPABASE_SERVICE_ROLE_KEY    (read-only use only — do not commit this)
  AI_JUDGE_PROVIDER            "anthropic" or "openai" — used only if you
                                want this script to also call a judge model
                                directly instead of separate RAGAS tooling.
                                Optional; leave unset to skip LLM judging
                                here and just produce the comparison table.

------------------------------------------------------------------
USAGE
------------------------------------------------------------------
  pip install -r requirements.txt
  export JUSTOR_BACKEND_URL=...
  export SUPABASE_URL=...
  export SUPABASE_SERVICE_ROLE_KEY=...
  python benchmark_harness.py --input justor_benchmark_verified_45.csv \
                               --output benchmark_results.csv \
                               --limit 5      # optional, test on a few rows first
"""

import argparse
import csv
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

from dotenv import load_dotenv
load_dotenv("../.env")
load_dotenv("../.env.local")

import requests

# ---------------------------------------------------------------------------
# Deterministic checks — no LLM involved, pure pattern/lookup logic
# ---------------------------------------------------------------------------

CITATION_TAG_RE = re.compile(r"\[(?:ACT|DLR)-\d+\]")
SECTION_CLAIM_RE = re.compile(
    r"(?:[Ss]ections?|[Aa]rticles?)\s+((?:\d+[A-Za-z]?(?:\(\d+\))?(?:\([a-zA-Z]\))?(?:\s*(?:,|and|to|-)\s*)?)+)"
)
DLR_CITATION_RE = re.compile(r"\d+\s*DLR\s*\(?[A-Za-z]*\)?\s*\d+", re.IGNORECASE)

INDIA_LEAKAGE_TERMS = [
    "indian penal code",
    " ipc ",
    "ipc,",
    "ipc.",
    "indian evidence act",
    "code of criminal procedure, 1973",
    "crpc 1973",
    "constitution of india",
    "indian constitution",
]


def check_fabricated_citation(answer_text: str, retrieved_tags: set[str]) -> dict:
    """Flags any [ACT-n] / [DLR-n] style tag cited in the answer that wasn't
    actually present in retrieved_sources. Requires the backend eval_mode
    contract above. If retrieved_tags is empty (contract not wired up yet),
    this check is skipped and marked NOT_AVAILABLE rather than guessed."""
    if not retrieved_tags:
        return {"fabricated_citation": "NOT_AVAILABLE", "fabricated_tags": []}
    cited = set(CITATION_TAG_RE.findall(answer_text))
    norm_retrieved = {t if t.startswith("[") else f"[{t}]" for t in retrieved_tags}
    fabricated = cited - norm_retrieved
    return {
        "fabricated_citation": bool(fabricated),
        "fabricated_tags": sorted(list(fabricated)),
    }


def check_dlr_case_exists(answer_text: str, known_dlr_citations: set[str]) -> dict:
    """Flags a DLR-style citation (e.g. '38 DLR (AD) 161') appearing in the
    answer text that doesn't match anything in the known DLR citation set
    pulled from document_chunks."""
    found = set(m.group(0).strip() for m in DLR_CITATION_RE.finditer(answer_text))
    if not known_dlr_citations:
        return {"unverifiable_dlr_citation": "NOT_AVAILABLE", "dlr_citations_found": sorted(list(found))}
    unverifiable = {c for c in found if c not in known_dlr_citations}
    return {
        "unverifiable_dlr_citation": bool(unverifiable),
        "dlr_citations_found": sorted(list(found)),
        "unverifiable_citations": sorted(list(unverifiable)),
    }


def check_wrong_section(answer_text: str, expected_act: str, expected_section: str,
                         db_lookup_fn=None) -> dict:
    """Compares section numbers claimed in the answer against the expected
    section for this question, handling subsection normalization (e.g., 96(1) matches 96)."""
    claimed_raw = SECTION_CLAIM_RE.findall(answer_text)
    claimed_sections = []
    for raw in claimed_raw:
        claimed_sections.extend(re.findall(r'\d+[A-Za-z]?(?:\(\d+\))?(?:\([a-zA-Z]\))?', raw))
    exp_mentioned = "N/A"
    if expected_section and str(expected_section).strip() and str(expected_section).strip().lower() != "nan":
        exp_str = str(expected_section).strip()
        exp_m = re.match(r'^(\d+[A-Za-z]?)', exp_str)
        exp_base = exp_m.group(1) if exp_m else exp_str

        claimed_bases = []
        for c in claimed_sections:
            cm = re.match(r'^(\d+[A-Za-z]?)', str(c))
            claimed_bases.append(cm.group(1) if cm else str(c))

        exp_mentioned = (
            any(exp_str.lower() == str(c).lower() for c in claimed_sections) or
            any(exp_base.lower() == str(cb).lower() for cb in claimed_bases)
        )

    result = {
        "claimed_sections": claimed_sections,
        "expected_section_mentioned": exp_mentioned,
    }
    if db_lookup_fn is not None:
        nonexistent = [s for s in claimed_sections if not db_lookup_fn(expected_act, s)]
        result["claimed_section_not_in_db"] = nonexistent
    else:
        return result


ACT_ADJACENCY_WHITELIST = {
    ('State Acquisition and Tenancy Act, 1950', 'Registration Act, 1908'),
    ('Transfer of Property Act, 1882', 'Registration Act, 1908'),
    ('Transfer of Property Act, 1882', 'Specific Relief Act, 1877'),
    ('Non-Agricultural Tenancy Act, 1949', 'State Acquisition and Tenancy Act, 1950'),
    ('Non-Agricultural Tenancy Act, 1949', 'Transfer of Property Act, 1882'),
    ('Land Reforms Act, 2023', 'State Acquisition and Tenancy Act, 1950'),
    ('Land Reforms Act, 2023', 'Registration Act, 1908'),
    ('Civil Courts Act, 1887', 'Code of Civil Procedure, 1908'),
    ('Penal Code, 1860', 'Code of Criminal Procedure, 1898'),
    ('Contract Act, 1872', 'Code of Civil Procedure, 1908'),
}

def is_whitelisted_adjacency(expected_act, other_act):
    for (a, b) in ACT_ADJACENCY_WHITELIST:
        a_key, b_key = a.split(',')[0], b.split(',')[0]
        if (a_key in expected_act and b_key in other_act) or \
           (b_key in expected_act and a_key in other_act):
            return True
    return False

def check_act_mismatch(answer_text: str, expected_act: str) -> dict:
    if not expected_act:
        return {"act_mismatch": "N/A"}
    exp_clean = re.sub(r'^(?:the\s+)', '', expected_act.strip(), flags=re.I)
    expected_options = [re.sub(r'^(?:the\s+)', '', opt.strip(), flags=re.I) for opt in exp_clean.split('/')]
    other_well_known_acts = [
        "Transfer of Property Act", "Code of Criminal Procedure",
        "Code of Civil Procedure", "Penal Code", "Limitation Act",
        "State Acquisition and Tenancy Act", "Non-Agricultural Tenancy Act",
        "Land Reforms Act", "Land Reforms Ordinance", "Income Tax Act",
        "Trademarks Act", "Muslim Family Laws Ordinance",
        "Hindu Women's Rights to Property Act", "Civil Courts Act",
        "Evidence Act", "Bangladesh Labour Act", "Registration Act",
        "Specific Relief Act"
    ]
    mentioned_other = []
    
    for a in other_well_known_acts:
        if a.lower() in answer_text.lower():
            is_expected = any(exp.split(",")[0].strip().lower() in a.lower() or a.lower() in exp.split(",")[0].strip().lower() for exp in expected_options)
            if not is_expected:
                is_whitelisted = any(is_whitelisted_adjacency(exp, a) for exp in expected_options)
                if not is_whitelisted:
                    mentioned_other.append(a)
                    
    return {"act_mismatch": bool(mentioned_other), "other_acts_mentioned": mentioned_other}


def check_jurisdiction_leakage(answer_text: str) -> dict:
    text = f" {answer_text.lower()} "
    hits = [t.strip() for t in INDIA_LEAKAGE_TERMS if t in text]
    return {"jurisdiction_leakage": bool(hits), "leaked_terms": hits}


def run_all_checks(answer_text: str, expected_act: str, expected_section: str,
                    retrieved_tags: set[str], known_dlr_citations: set[str]) -> dict:
    out = {}
    out.update(check_fabricated_citation(answer_text, retrieved_tags))
    out.update(check_dlr_case_exists(answer_text, known_dlr_citations))
    out.update(check_wrong_section(answer_text, expected_act, expected_section))
    out.update(check_act_mismatch(answer_text, expected_act))
    out.update(check_jurisdiction_leakage(answer_text))
    tags_found = CITATION_TAG_RE.findall(answer_text)
    dlr_found = [m.group(0).strip() for m in DLR_CITATION_RE.finditer(answer_text)]
    out["citations_found"] = sorted(list(set(tags_found + dlr_found)))
    return out


# ---------------------------------------------------------------------------
# Backend call
# ---------------------------------------------------------------------------

@dataclass
class ChatResult:
    answer_text: str = ""
    retrieved_tags: set = field(default_factory=set)
    retrieved_contexts: list = field(default_factory=list)
    raw_response: dict = field(default_factory=dict)
    error: Optional[str] = None


def call_chat_endpoint(backend_url: str, question: str, timeout: int = 240) -> ChatResult:
    url = backend_url.rstrip("/") + "/chat"
    payload = {
        "message": question,
        "user_id": "benchmark-harness",
        "role": "General Public",
        "history": [],
        "eval_mode": True,
    }
    last_err = None
    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            answer_text = data.get("response", "")
            sources = data.get("retrieved_sources", [])  # only present if backend supports eval_mode
            tags = {s.get("tag") or f"[{s.get('id')}]" for s in sources if s.get("tag") or s.get("id")}
            contexts = [s.get("content") or s.get("ratio_decidendi") or "" for s in sources]
            return ChatResult(
                answer_text=answer_text,
                retrieved_tags=tags,
                retrieved_contexts=contexts,
                raw_response=data,
            )
        except Exception as e:
            last_err = str(e)
            if attempt < 2:
                print(f"  [Retry {attempt + 1}] Network/API error: {e}. Retrying in 5s...")
                time.sleep(5)
    return ChatResult(error=str(last_err))


# ---------------------------------------------------------------------------
# Optional: known DLR citations pulled from Supabase, for check_dlr_case_exists.
# Falls back to an empty set (check marked NOT_AVAILABLE) if Supabase env vars
# are not set or the supabase package isn't installed.
# ---------------------------------------------------------------------------

def load_known_dlr_citations() -> set[str]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return set()
    try:
        from supabase import create_client
    except ImportError:
        print("WARNING: supabase package not installed; pip install supabase to "
              "enable the DLR-citation-exists check. Skipping for now.", file=sys.stderr)
        return set()
    try:
        def db_lookup_fn(act_name: str, sec: str) -> bool:
            try:
                # Use ilike to handle slight act name mismatches (e.g. missing 'The ')
                resp = supabase.table("document_chunks") \
                    .select("id") \
                    .ilike("act_name", f"%{act_name}%") \
                    .eq("section_number", str(sec)) \
                    .execute()
                return len(resp.data) > 0
            except Exception as e:
                print(f"DB lookup error: {e}")
                return False
        client = create_client(url, key)
        rows = (
            client.table("document_chunks")
            .select("case_title, year, court_division, metadata")
            .eq("document_type", "DLR")
            .execute()
        )
        citations = set()
        for r in rows.data or []:
            meta = r.get("metadata") or {}
            cit = meta.get("citation")
            if cit:
                citations.add(cit)
        return citations
    except Exception as e:
        print(f"WARNING: could not load DLR citations from Supabase ({e}). "
              f"DLR citation check will be NOT_AVAILABLE.", file=sys.stderr)
        return set()


# ---------------------------------------------------------------------------
# Optional: RAGAS scoring — best-effort, clearly marked if unavailable.
# RAGAS's API has changed across versions; if this block errors on your
# installed version, the script still produces the deterministic-check
# table below — RAGAS columns will just read NOT_AVAILABLE.
# ---------------------------------------------------------------------------

def try_ragas_score(question: str, answer: str, contexts: list[str],
                     reference: str) -> dict:
    if not contexts:
        return {
            "faithfulness": "NOT_AVAILABLE",
            "answer_relevancy": "NOT_AVAILABLE",
            "context_precision": "NOT_AVAILABLE",
            "context_recall": "NOT_AVAILABLE",
            "ragas_note": "no retrieved_contexts returned by backend (eval_mode not wired up yet?)",
        }
    try:
        import sys
        from unittest.mock import MagicMock
        sys.modules['langchain_community.chat_models.vertexai'] = MagicMock()
        sys.modules['langchain_community.chat_models'] = MagicMock()
        sys.modules['langchain_community.llms'] = MagicMock()
        sys.modules['langchain_community.llms.vertexai'] = MagicMock()
        
        from ragas import evaluate, EvaluationDataset
        from ragas.metrics import (
            Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall,
        )
        import os
        from langchain_openai import ChatOpenAI
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        judge_llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        judge_embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2", 
            google_api_key=os.environ.get("GEMINI_API_KEY")
        )
        
        sample = {
            "user_input": question,
            "response": answer,
            "retrieved_contexts": contexts,
            "reference": reference,
        }
        ds = EvaluationDataset.from_list([sample])
        result = evaluate(
            ds,
            metrics=[Faithfulness(), AnswerRelevancy(), ContextPrecision(), ContextRecall()],
            llm=judge_llm,
            embeddings=judge_embeddings
        )
        df = result.to_pandas()
        row = df.iloc[0]
        return {
            "faithfulness": row.get("faithfulness", "NOT_AVAILABLE"),
            "answer_relevancy": row.get("answer_relevancy", "NOT_AVAILABLE"),
            "context_precision": row.get("context_precision", "NOT_AVAILABLE"),
            "context_recall": row.get("context_recall", "NOT_AVAILABLE"),
            "ragas_note": "",
        }
    except Exception as e:
        return {
            "faithfulness": "NOT_AVAILABLE",
            "answer_relevancy": "NOT_AVAILABLE",
            "context_precision": "NOT_AVAILABLE",
            "context_recall": "NOT_AVAILABLE",
            "ragas_note": f"RAGAS call failed: {e}. Check installed ragas version "
                          f"against this script's API usage.",
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="justor_benchmark_verified_45.csv")
    ap.add_argument("--output", default="benchmark_results.csv")
    ap.add_argument("--limit", type=int, default=None,
                     help="Run only the first N rows — use this first.")
    ap.add_argument("--skip-ragas", action="store_true",
                     help="Skip RAGAS entirely, only run deterministic checks "
                          "(fast, no extra API cost).")
    ap.add_argument("--resume", action="store_true",
                     help="Resume from existing output CSV without deleting it or re-running completed IDs.")
    args = ap.parse_args()

    backend_url = os.environ.get("JUSTOR_BACKEND_URL")
    if not backend_url:
        print("ERROR: set JUSTOR_BACKEND_URL env var "
              "(e.g. https://justorai-backend.onrender.com)", file=sys.stderr)
        sys.exit(1)

    known_dlr_citations = load_known_dlr_citations()

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]

    completed_ids = set()
    if args.resume and os.path.exists(args.output) and os.path.getsize(args.output) > 0:
        try:
            with open(args.output, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r.get("id"):
                        completed_ids.add(r["id"])
            print(f"Resuming: found {len(completed_ids)} completed questions in {args.output}")
        except Exception as e:
            print(f"Warning: could not read existing output for resume ({e}). Starting fresh.")
    elif os.path.exists(args.output):
        os.remove(args.output)

    out_rows = []
    for i, row in enumerate(rows, 1):
        qid = row["id"]
        if args.resume and qid in completed_ids:
            print(f"[{i}/{len(rows)}] {qid}: ALREADY COMPLETED (skipping)")
            continue
        question = row["question"]
        gold = row["gold_answer"]
        expected_act = row.get("expected_act", "")
        expected_section = row.get("expected_section", "")

        print(f"[{i}/{len(rows)}] {qid}: {question[:70]}...")

        chat = call_chat_endpoint(backend_url, question)
        if chat.error:
            out_rows.append({
                "id": qid, "question": question, "gold_answer": gold,
                "system_answer": "", "error": chat.error,
            })
            continue

        checks = run_all_checks(
            chat.answer_text, expected_act, expected_section,
            chat.retrieved_tags, known_dlr_citations,
        )

        ragas_scores = {}
        if not args.skip_ragas:
            ragas_scores = try_ragas_score(
                question, chat.answer_text, chat.retrieved_contexts, gold
            )

        row_res = {
            "id": qid,
            "category": row.get("category", ""),
            "question": question,
            "gold_answer": gold,
            "system_answer": chat.answer_text,
            "expected_act": expected_act,
            "expected_section": expected_section,
            **checks,
            **ragas_scores,
            "human_correctness": row.get("human_correctness", ""),
            "human_faithfulness": row.get("human_faithfulness", ""),
            "judge_agrees_with_human": row.get("judge_agrees_with_human", ""),
            "notes": row.get("notes", ""),
        }
        out_rows.append(row_res)
        file_exists = os.path.exists(args.output) and os.path.getsize(args.output) > 0
        with open(args.output, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(row_res.keys()))
            if not file_exists:
                w.writeheader()
            w.writerow(row_res)
        time.sleep(8)  # 8s between questions — prevents Gemini embedding API quota exhaustion

    flagged = [r for r in out_rows if r.get("fabricated_citation") is True
               or r.get("act_mismatch") is True
               or r.get("jurisdiction_leakage") is True
               or r.get("unverifiable_dlr_citation") is True]
    print(f"\nDone. {len(out_rows)} rows written to {args.output}")
    print(f"{len(flagged)} rows flagged by deterministic checks — review these first.")


if __name__ == "__main__":
    main()
