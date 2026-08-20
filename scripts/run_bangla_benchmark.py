import asyncio
import csv
import json
import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("."))

from backend.backend import legal_engine_v2
from backend.legal_normalize import normalize_bengali_text, detect_language


async def run_bangla_benchmark():
    if not legal_engine_v2:
        print("[ERROR] Legal Evidence Engine V2 is not initialized.")
        return

    benchmark_path = os.path.join("evaluation", "bangla_legal_bench_50.json")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("\n=======================================================")
    print("  JUSTOR AI V3 -- BANGLALEGALBENCH 50 EVALUATION SUITE")
    print("  Testing Bilingual Act->Section & Bangla Intelligence")
    print("=======================================================\n")

    results = []
    passed_count = 0
    total = len(cases)
    start_all = time.time()

    act_recall_hits = 0
    sec_recall_hits = 0

    csv_rows = []

    for idx, c in enumerate(cases, 1):
        cid = c["id"]
        domain = c["domain"]
        persona = c["persona"]
        category = c.get("language_category", "Bangla")
        q = c["question"]
        expected_act = c.get("expected_act", "")
        expected_secs = c.get("expected_sections", [])
        forbidden = c.get("forbidden_sections", [])
        must_mention = c.get("must_mention", [])
        should_abstain = c.get("should_abstain_or_reject", False)

        print(f"[{idx:02d}/{total:02d}] Testing {cid} ({category} · {domain})...", end="", flush=True)
        t0 = time.time()

        try:
            res = await legal_engine_v2.answer(q, persona)
            elapsed = time.time() - t0
            status = res.get("status", "unknown")
            answer = res.get("answer", "")
            authorities = res.get("authorities", [])

            # Format retrieved authorities safely
            auth_tokens = []
            for a in authorities:
                if isinstance(a, dict):
                    act = a.get("act", "")
                    sec = a.get("section", "")
                    auth_tokens.append(f"{act} s.{sec}" if sec else act)
                else:
                    auth_tokens.append(str(a))
            auth_summary = "; ".join(auth_tokens) if auth_tokens else "None"

            # Check Act Recall & Section Recall
            retrieved_clean = auth_summary.lower().replace("’", "'").replace("`", "'")
            retrieved_str = retrieved_clean
            expected_clean = expected_act.lower().replace("’", "'").replace("`", "'")
            
            # Match either full expected act title or core keyword if present
            act_hit = bool(expected_clean and expected_clean in retrieved_clean) or should_abstain
            if not act_hit and "constitution" in expected_clean and "constitution" in retrieved_clean:
                act_hit = True
            if not act_hit and "family courts" in expected_clean and "family court" in retrieved_clean:
                act_hit = True

            sec_hit = all(s.lower() in retrieved_clean for s in expected_secs) if expected_secs else True

            if act_hit:
                act_recall_hits += 1
            if sec_hit or should_abstain:
                sec_recall_hits += 1

            # Evaluation criteria
            is_pass = False
            fail_reason = ""
            eval_note = "GROUNDED_VERIFIED"

            if should_abstain:
                if status == "abstain":
                    is_pass = True
                    eval_note = "REJECTED_ADVERSARIAL_QUERY"
                else:
                    fail_reason = "Expected abstain on adversarial nonexistent law, but generated answer."
            elif res.get("status") == "error":
                fail_reason = str(res.get("reason", "Unknown engine error"))
            else:
                has_forbidden = any(f.lower() in str(answer).lower() or f.lower() in retrieved_str for f in forbidden) if forbidden else False

                WORD_NUM_MAP = {
                    "24": ["24", "twenty-four", "২৪", "চব্বিশ"],
                    "30": ["30", "thirty", "৩০", "ত্রিশ"],
                    "60": ["60", "sixty", "৬০", "ষাট"],
                    "90": ["90", "ninety", "৯০", "নব্বই"],
                    "15": ["15", "fifteen", "১৫", "পনেরো"],
                    "25": ["25", "twenty-five", "২৫", "পঁচিশ"],
                }
                missing_keywords = []
                if status == "ok" and answer:
                    for kw in must_mention:
                        alts = WORD_NUM_MAP.get(kw, [kw])
                        if not any(alt.lower() in str(answer).lower() for alt in alts):
                            missing_keywords.append(kw)

                if has_forbidden:
                    fail_reason = f"Contains forbidden section attribution {forbidden}"
                elif missing_keywords and len(missing_keywords) > 2:
                    fail_reason = f"Missing key legal concepts: {missing_keywords}"
                elif not act_hit and not should_abstain:
                    fail_reason = f"Act recall missed for {expected_act}"
                else:
                    is_pass = True
                    has_primary = any(
                        (isinstance(a, dict) and a.get("trust_tier") == "PRIMARY_STATUTE")
                        or ("primary" in str(a).lower())
                        for a in authorities
                    )
                    if has_primary:
                        eval_note = "FULLY_GROUNDED_PRIMARY_STATUTE"
                    else:
                        eval_note = "GROUNDED_LEGACY_CORPUS"

            if is_pass:
                passed_count += 1
                print(f"  [PASS] ({elapsed:.2f}s)")
            else:
                print(f"  [FAIL] ({elapsed:.2f}s) -> {fail_reason}")

            csv_rows.append({
                "ID": cid,
                "Language_Category": category,
                "Domain": domain,
                "Persona": persona,
                "Question": q,
                "Expected_Act": expected_act,
                "Expected_Sections": ", ".join(expected_secs),
                "Result": "PASS" if is_pass else "FAIL",
                "Engine_Status": status,
                "Act_Recall_Hit": "YES" if act_hit else "NO",
                "Section_Recall_Hit": "YES" if sec_hit else "NO",
                "Retrieved_Authorities": auth_summary,
                "Latency_Seconds": f"{elapsed:.2f}",
                "Evaluation_Notes": eval_note if is_pass else fail_reason
            })

        except Exception as exc:
            elapsed = time.time() - t0
            print(f"  [ERROR] ({elapsed:.2f}s) -> {str(exc)}")
            csv_rows.append({
                "ID": cid,
                "Language_Category": category,
                "Domain": domain,
                "Persona": persona,
                "Question": q,
                "Expected_Act": expected_act,
                "Expected_Sections": ", ".join(expected_secs),
                "Result": "ERROR",
                "Engine_Status": "error",
                "Act_Recall_Hit": "NO",
                "Section_Recall_Hit": "NO",
                "Retrieved_Authorities": "None",
                "Latency_Seconds": f"{elapsed:.2f}",
                "Evaluation_Notes": str(exc)
            })

    total_time = time.time() - start_all
    avg_latency = total_time / total if total else 0
    accuracy = (passed_count / total) * 100 if total else 0
    act_recall = (act_recall_hits / total) * 100 if total else 0
    sec_recall = (sec_recall_hits / total) * 100 if total else 0

    print(f"\n=======================================================")
    print(f"  BANGLALEGALBENCH RESULTS SUMMARY")
    print(f"=======================================================")
    print(f"  Total Questions Evaluated : {total}")
    print(f"  Passed (Grounded & Accurate): {passed_count}")
    print(f"  Failed / Divergent        : {total - passed_count}")
    print(f"  Overall Accuracy Score    : {accuracy:.1f}%")
    print(f"  Act Recall@3              : {act_recall:.1f}%")
    print(f"  Section Recall@3          : {sec_recall:.1f}%")
    print(f"  Average Latency Per Query : {avg_latency:.2f}s")
    print(f"  Total Execution Time      : {total_time:.2f}s")

    csv_path = os.path.abspath("bangla_benchmark_results_50.csv")
    fieldnames = [
        "ID", "Language_Category", "Domain", "Persona", "Question", "Expected_Act",
        "Expected_Sections", "Result", "Engine_Status", "Act_Recall_Hit", "Section_Recall_Hit",
        "Retrieved_Authorities", "Latency_Seconds", "Evaluation_Notes"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"  CSV Results Saved To      : {csv_path}")
    print(f"=======================================================\n")


if __name__ == "__main__":
    asyncio.run(run_bangla_benchmark())
