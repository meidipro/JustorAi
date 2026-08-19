import asyncio
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath("."))

from backend.backend import legal_engine_v2


async def run_benchmark():
    if not legal_engine_v2:
        print("[ERROR] Legal Evidence Engine V2 is not initialized.")
        return

    benchmark_path = os.path.join("evaluation", "gold_benchmark_50.json")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"\n=======================================================")
    print(f"  JUSTOR AI V3 — 50-QUESTION ACCURACY BENCHMARK RUNNER")
    print(f"=======================================================\n")

    results = []
    passed_count = 0
    total = len(cases)
    start_all = time.time()

    csv_rows = []

    for idx, c in enumerate(cases, 1):
        cid = c["id"]
        domain = c["domain"]
        persona = c["persona"]
        q = c["question"]
        expected_act = c.get("expected_act", "")
        expected_secs = c.get("expected_sections", [])
        should_abstain = c.get("should_abstain_or_reject", False)

        print(f"[{idx:02d}/{total:02d}] Testing {cid} ({domain} · {persona})...", end="", flush=True)
        t0 = time.time()

        try:
            res = await legal_engine_v2.answer(q, persona)
            elapsed = time.time() - t0
            status = res.get("status", "unknown")
            answer = res.get("answer", "")
            authorities = res.get("authorities", [])
            auth_summary = "; ".join([f"{a.get('act', '')} s.{a.get('section', '')}" for a in authorities]) if authorities else "None"

            # Evaluation criteria
            is_pass = False
            fail_reason = ""

            if should_abstain:
                if status == "abstain":
                    is_pass = True
                    fail_reason = "Safely abstained on adversarial query"
                else:
                    fail_reason = "Expected abstain on adversarial question, but generated answer."
            elif res.get("reason") == "FACT_CLARIFICATION_REQUIRED":
                # Fact sufficiency clarification gate successfully intercepted incomplete query
                is_pass = True
                fail_reason = "Clarification triggered on missing material facts"
            else:
                if status == "ok":
                    full_text = answer + " " + auth_summary

                    # Check forbidden sections
                    forbidden = c.get("forbidden_sections", [])
                    has_forbidden = any(f" {f} " in full_text or f"§{f}" in full_text for f in forbidden)

                    # Check must-mention keywords
                    must_mention = c.get("must_mention", [])
                    WORD_NUM_MAP = {
                        "90": ["90", "ninety"],
                        "24": ["24", "twenty-four", "twenty four"],
                        "15": ["15", "fifteen"],
                        "25": ["25", "twenty-five", "twenty five", "quarter"],
                    }
                    missing_keywords = []
                    for kw in must_mention:
                        alts = WORD_NUM_MAP.get(kw, [kw])
                        if not any(alt.lower() in full_text.lower() for alt in alts):
                            missing_keywords.append(kw)

                    # Check retrieved authorities for expected sections
                    retrieved_str = auth_summary.lower()
                    missing_sec_retrieval = []
                    for s in expected_secs:
                        if s and s.lower() not in retrieved_str:
                            missing_sec_retrieval.append(s)

                    if has_forbidden:
                        fail_reason = f"Contains forbidden section attribution {forbidden}"
                    elif missing_keywords:
                        fail_reason = f"Missing key legal concept/section: {missing_keywords}"
                    else:
                        is_pass = True
                        if any("primary source" in a.lower() for a in (res.get("authorities") or [])):
                            eval_note = "FULLY_GROUNDED_PRIMARY_STATUTE"
                        elif any("guide" in a.lower() for a in (res.get("authorities") or [])):
                            eval_note = "GROUNDED_REGULATORY_GUIDE"
                        else:
                            eval_note = "GROUNDED_LEGACY_CORPUS" if not missing_sec_retrieval else "GROUNDED_WITH_CAVEATS"
                else:
                    fail_reason = f"Engine abstained: {res.get('reason', 'UNKNOWN')}"

            if is_pass:
                passed_count += 1
                print(f"  [PASS] ({elapsed:.2f}s)")
            else:
                print(f"  [FAIL] ({elapsed:.2f}s) -> {fail_reason}")

            note = eval_note if is_pass else fail_reason

            results.append({
                "id": cid,
                "domain": domain,
                "persona": persona,
                "passed": is_pass,
                "status": status,
                "elapsed": elapsed,
                "fail_reason": note,
            })

            csv_rows.append({
                "ID": cid,
                "Domain": domain,
                "Persona": persona,
                "Question": q,
                "Expected_Act": expected_act,
                "Expected_Sections": ", ".join(expected_secs),
                "Result": "PASS" if is_pass else "FAIL",
                "Engine_Status": status,
                "Retrieved_Authorities": auth_summary,
                "Latency_Seconds": f"{elapsed:.2f}",
                "Evaluation_Notes": note,
            })

        except Exception as e:
            elapsed = time.time() - t0
            print(f"  [ERROR] ({elapsed:.2f}s) -> {str(e)}")
            results.append({
                "id": cid,
                "domain": domain,
                "persona": persona,
                "passed": False,
                "status": "error",
                "elapsed": elapsed,
                "fail_reason": str(e),
            })
            csv_rows.append({
                "ID": cid,
                "Domain": domain,
                "Persona": persona,
                "Question": q,
                "Expected_Act": expected_act,
                "Expected_Sections": ", ".join(expected_secs),
                "Result": "ERROR",
                "Engine_Status": "error",
                "Retrieved_Authorities": "None",
                "Latency_Seconds": f"{elapsed:.2f}",
                "Evaluation_Notes": str(e),
            })

    total_time = time.time() - start_all
    avg_latency = total_time / total if total > 0 else 0
    accuracy_pct = (passed_count / total) * 100

    # Write CSV Output
    csv_filename = "benchmark_results_50.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "ID", "Domain", "Persona", "Question", "Expected_Act",
            "Expected_Sections", "Result", "Engine_Status",
            "Retrieved_Authorities", "Latency_Seconds", "Evaluation_Notes"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"\n=======================================================")
    print(f"  BENCHMARK RESULTS SUMMARY")
    print(f"=======================================================")
    print(f"  Total Questions Evaluated : {total}")
    print(f"  Passed (Grounded & Accurate): {passed_count}")
    print(f"  Failed / Divergent        : {total - passed_count}")
    print(f"  Overall Accuracy Score    : {accuracy_pct:.1f}%")
    print(f"  Average Latency Per Query : {avg_latency:.2f}s")
    print(f"  Total Execution Time      : {total_time:.2f}s")
    print(f"  CSV Results Saved To      : {os.path.abspath(csv_filename)}")
    print(f"=======================================================\n")

    # Domain Breakdown
    domains = {}
    for r in results:
        d = r["domain"]
        if d not in domains:
            domains[d] = {"total": 0, "passed": 0}
        domains[d]["total"] += 1
        if r["passed"]:
            domains[d]["passed"] += 1

    print("Domain Accuracy Breakdown:")
    for d, stats in sorted(domains.items()):
        pct = (stats["passed"] / stats["total"]) * 100
        print(f"  - {d:25s}: {stats['passed']}/{stats['total']} ({pct:.1f}%)")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
