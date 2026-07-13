# Justor AI Benchmark Pack

## Files

| File | Use |
|---|---|
| `justor_benchmark_verified_45.csv` | 45 questions + gold answers, ready to run now. Sourced from Bug.md / Bug report 2.md / Response report justor(1).md — all have a confirmed, traceable source answer. |
| `justor_benchmark_needs_verification_14.csv` | 12 questions whose gold answer was AI-drafted (no original source answer existed) + 2 whose source answer was flagged as mismatched to the question. Do **not** use these in an official run until Sanjib or a lawyer confirms each `draft_gold_answer` against the actual statute/case text. Two rows (Q20, Q52) also have a `MISMATCH WARNING` note — the feedback attached to them in the source material doesn't match the question; flag this to whoever compiled the original reports. |
| `benchmark_harness.py` | Runs the 45 against `/chat`, applies deterministic legal-safety checks, and (if available) scores RAGAS metrics. |
| `requirements.txt` | Python deps for the harness — install in its own venv, don't merge into backend/requirements.txt. |

## What Mehedi needs to do first

The harness's deterministic checks (fabricated citation, wrong section, act mismatch) work much better if `/chat` returns what it actually retrieved. See the docstring at the top of `benchmark_harness.py` for the exact contract — short version: accept an optional `"eval_mode": true` in the request, and when set, also return `"retrieved_sources": [...]` listing the Act/section or DLR case each numbered tag (`[ACT-1]`, `[DLR-1]`) refers to.

Without this change, the script still runs and still produces a comparison table — it just can't confirm whether a cited tag was actually retrieved, and RAGAS context metrics (which need to see what was retrieved) will show `NOT_AVAILABLE` instead of a number.

## How to run

```bash
pip install -r requirements.txt
export JUSTOR_BACKEND_URL=https://justorai-backend.onrender.com
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...

# test on 3 rows first, skip RAGAS to check the deterministic checks fire correctly
python benchmark_harness.py --limit 3 --skip-ragas

# full run once that looks right
python benchmark_harness.py
```

Output: `benchmark_results.csv` — gold answer, system answer, every deterministic flag, RAGAS scores (or `NOT_AVAILABLE`), and blank `human_correctness` / `human_faithfulness` / `judge_agrees_with_human` columns for Sanjib to fill in by hand. Sort by the flagged columns first — those are the rows worth looking at before anything else.

## Reminder on how to read the output

- A clean RAGAS score on a row that's also flagged by a deterministic check means **trust the deterministic check, not the RAGAS score** — that's the exact failure mode found in the original 5-row CSV (Faithfulness 1.0 on a row with a fabricated case citation).
- This 45-question set is drawn entirely from known past bug reports — treat results from it as a regression/stress-test signal, not a representative "X% accurate" claim. Build a second, randomly-sampled question set from real beta-user queries before making any external accuracy claim.

## Process Rule: Single Source of Truth for Human Evaluation
Sanjib's human review verdicts (`PASS` / `PARTIAL` / `FAIL`) must be recorded **directly into the `human_correctness` column** of the benchmark CSV going forward, rather than maintained in a separate side file. The benchmark harness (`benchmark harness.py`) preserves existing `human_correctness` entries across runs so manual evaluations are permanently maintained in the canonical CSV file.
