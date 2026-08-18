import asyncio
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
    print(f"  JUSTOR AI — 50-QUESTION LEGAL ACCURACY BENCHMARK")
    print(f"=======================================================\n")

    results = []
    passed_count = 0
    total = len(cases)
    start_all = time.time()

    for idx, c in enumerate(cases, 1):
        cid = c["id"]
        domain = c["domain"]
        persona = c["persona"]
        q = c["question"]
        expected_act = c.get("expected_act")
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

            # Evaluation criteria
            is_pass = False
            fail_reason = ""

            if should_abstain:
                if status == "abstain":
                    is_pass = True
                else:
                    fail_reason = "Expected abstain on adversarial question, but generated answer."
            else:
                if status == "ok":
                    # Check statutory authority match
                    auth_texts = " ".join([a.get("act", "") + " " + a.get("section", "") for a in authorities])
                    full_text = answer + " " + auth_texts

                    # Check forbidden sections
                    forbidden = c.get("forbidden_sections", [])
                    has_forbidden = any(f" {f} " in full_text or f"§{f}" in full_text for f in forbidden)

                    # Check must-mention keywords
                    must_mention = c.get("must_mention", [])
                    missing_keywords = [kw for kw in must_mention if kw.lower() not in full_text.lower()]

                    if has_forbidden:
                        fail_reason = f"Contains forbidden section attribution {forbidden}"
                    elif missing_keywords:
                        fail_reason = f"Missing key legal concept/section: {missing_keywords}"
                    else:
                        is_pass = True
                else:
                    fail_reason = f"Engine abstained: {res.get('reason', 'UNKNOWN')}"

            if is_pass:
                passed_count += 1
                print(f"  [PASS] ({elapsed:.2f}s)")
            else:
                print(f"  [FAIL] ({elapsed:.2f}s) -> {fail_reason}")

            results.append({
                "id": cid,
                "domain": domain,
                "persona": persona,
                "passed": is_pass,
                "status": status,
                "elapsed": elapsed,
                "fail_reason": fail_reason,
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

    total_time = time.time() - start_all
    avg_latency = total_time / total if total > 0 else 0
    accuracy_pct = (passed_count / total) * 100

    print(f"\n=======================================================")
    print(f"  BENCHMARK RESULTS SUMMARY")
    print(f"=======================================================")
    print(f"  Total Questions Evaluated : {total}")
    print(f"  Passed (Grounded & Accurate): {passed_count}")
    print(f"  Failed / Divergent        : {total - passed_count}")
    print(f"  Overall Accuracy Score    : {accuracy_pct:.1f}%")
    print(f"  Average Latency Per Query : {avg_latency:.2f}s")
    print(f"  Total Execution Time      : {total_time:.2f}s")
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
