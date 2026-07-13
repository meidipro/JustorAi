import os
import sys
import time
import subprocess
import urllib.request
import pandas as pd

def main():
    print("=== Launching Local Backend Server for Pilot-Launch v16 FINAL Benchmark ===")
    py_cmd = os.path.abspath(".venv/Scripts/python.exe") if os.path.exists(".venv/Scripts/python.exe") else sys.executable
    print(f"Using Python interpreter: {py_cmd}")

    log_file = open("backend_benchmark_v16.log", "w", encoding="utf-8")
    backend_proc = subprocess.Popen(
        [py_cmd, "-m", "uvicorn", "backend.backend:app", "--host", "127.0.0.1", "--port", "10001"],
        stdout=log_file,
        stderr=log_file
    )

    ready = False
    for attempt in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:10001/ping", timeout=2) as res:
                if res.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(1)

    if not ready:
        print("ERROR: Backend server failed to start within 30 seconds.")
        log_file.close()
        backend_proc.terminate()
        sys.exit(1)

    print("Backend server ready at http://127.0.0.1:10001")
    print("=== Running Complete 45-Question v16 FINAL Benchmark Harness ===")

    env = os.environ.copy()
    env["JUSTOR_BACKEND_URL"] = "http://127.0.0.1:10001"

    out_file = "brenchmark/benchmark_results_pilot_launch_v16_final.csv"
    harness_cmd = [
        py_cmd,
        "brenchmark/benchmark harness.py",
        "--input", "brenchmark/justor benchmark verified 45.csv",
        "--output", out_file,
        "--skip-ragas"
    ]

    try:
        subprocess.run(harness_cmd, env=env, check=True)
    finally:
        print("\nStopping local backend server...")
        backend_proc.terminate()
        backend_proc.wait()
        log_file.close()

    if os.path.exists(out_file):
        df = pd.read_csv(out_file)
        print("\n================================================")
        print("  JUSTOR AI PILOT-LAUNCH v16 FINAL BENCHMARK    ")
        print("================================================")
        total = len(df)
        http500 = df['system_answer'].str.contains('HTTP 500|Internal Server Error|HTTPError', case=False, na=False).sum()
        http503 = df['system_answer'].str.contains('HTTP 503|service busy|service unavailable', case=False, na=False).sum()
        not_found = df['system_answer'].str.contains('not locate|not in my verified|HTTP 503', case=False, na=False).sum()
        dlr_cites = df['system_answer'].str.contains('DLR-', case=False, na=False).sum()

        def is_true(val):
            if isinstance(val, bool): return val
            if isinstance(val, str): return val.strip().lower() == 'true'
            return False

        fab_cit = df['fabricated_citation'].apply(is_true).sum()
        act_mis = df['act_mismatch'].apply(is_true).sum()
        jur_leak = df['jurisdiction_leakage'].apply(is_true).sum()
        sec_hits = df['expected_section_mentioned'].apply(is_true).sum()
        sec_eval_total = df['expected_section'].notna().sum()

        clean_mask = ~(
            df['system_answer'].str.contains('HTTP 500|Internal Server Error|HTTPError|not locate|not in my verified|HTTP 503', case=False, na=False) |
            df['fabricated_citation'].apply(is_true) |
            df['act_mismatch'].apply(is_true) |
            df['jurisdiction_leakage'].apply(is_true)
        )
        clean_count = clean_mask.sum()
        pass_rate = (clean_count / total) * 100 if total > 0 else 0
        sec_hit_rate = (sec_hits / sec_eval_total) * 100 if sec_eval_total > 0 else 0
        mismatch_pct = (act_mis / total) * 100 if total > 0 else 0

        print(f"Total Questions Evaluated:   {total}")
        print(f"HTTP 503 Crashes / Busy:     {http503}")
        print(f"HTTP 500 Server Errors:      {http500}")
        print(f"Not Found in Knowledge Base: {not_found}")
        print(f"DLR Case Law Cited:          {dlr_cites} questions ({dlr_cites}/{total})")
        print(f"Exact Section Hit Rate:      {sec_hit_rate:.1f}% ({sec_hits}/{sec_eval_total})")
        print(f"Fabricated Citations:        {fab_cit}")
        print(f"Act Mismatches:              {act_mis} ({mismatch_pct:.1f}%)")
        print(f"Jurisdiction Leakage:        {jur_leak} (Strict Bangladesh Law)")
        print("------------------------------------------------")
        print(f"v16 FINAL PILOT PASS RATE:   {pass_rate:.1f}% ({clean_count}/{total})")
        print("================================================\n")
        print(f"Saved to: {out_file}")

if __name__ == "__main__":
    main()
