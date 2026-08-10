import os
import sys
import time
import subprocess
import urllib.request
import pandas as pd

def main():
    print("=== Launching Local Backend Server for 50-Question Benchmark ===")
    py_cmd = os.path.abspath(".venv/Scripts/python.exe") if os.path.exists(".venv/Scripts/python.exe") else sys.executable
    print(f"Using Python interpreter: {py_cmd}")

    log_file = open("backend_benchmark.log", "w", encoding="utf-8")
    backend_proc = subprocess.Popen(
        [py_cmd, "-m", "uvicorn", "backend.backend:app", "--host", "127.0.0.1", "--port", "10000"],
        stdout=log_file,
        stderr=log_file
    )

    # Wait for server /ping healthcheck
    ready = False
    for attempt in range(25):
        try:
            with urllib.request.urlopen("http://127.0.0.1:10000/ping", timeout=2) as res:
                if res.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(1)

    if not ready:
        print("ERROR: Backend server failed to start within 25 seconds.")
        log_file.close()
        if os.path.exists("backend_benchmark.log"):
            with open("backend_benchmark.log", "r", encoding="utf-8") as f:
                print("--- Backend Log Output ---")
                print(f.read())
        backend_proc.terminate()
        sys.exit(1)

    print("Backend server ready at http://127.0.0.1:10000")
    print("=== Running 50-Question Benchmark Harness ===")

    env = os.environ.copy()
    env["JUSTOR_BACKEND_URL"] = "http://127.0.0.1:10000"

    harness_cmd = [
        py_cmd,
        "brenchmark/benchmark harness.py",
        "--input", "brenchmark/justor_benchmark_50.csv",
        "--output", "brenchmark/benchmark_results_50.csv",
        "--skip-ragas"
    ]

    try:
        subprocess.run(harness_cmd, env=env, check=True)
    finally:
        print("\nStopping local backend server...")
        backend_proc.terminate()
        backend_proc.wait()
        log_file.close()

    # Calculate and display summary statistics
    res_file = "brenchmark/benchmark_results_50.csv"
    if os.path.exists(res_file):
        df = pd.read_csv(res_file)
        print("\n================================================")
        print("        JUSTOR AI 50-QUESTION BENCHMARK RESULTS  ")
        print("================================================")
        total = len(df)
        def is_true(val):
            if isinstance(val, bool): return val
            if isinstance(val, str): return val.strip().lower() == 'true'
            return False

        fab_cit = df['fabricated_citation'].apply(is_true).sum()
        act_mis = df['act_mismatch'].apply(is_true).sum()
        http500 = df['system_answer'].str.contains(r'500 Server Error|Internal Server Error|HTTPError|\b503 Server Error\b', case=False, na=False).sum()
        not_found = df['system_answer'].str.contains('not locate|not in my verified database', case=False, na=False).sum()

        jur_leak = df['jurisdiction_leakage'].apply(is_true).sum()
        unv_dlr = df['unverifiable_dlr_citation'].apply(is_true).sum()

        clean_mask = ~(
            df['system_answer'].str.contains(r'500 Server Error|Internal Server Error|HTTPError|not locate|not in my verified database', case=False, na=False) |
            df['fabricated_citation'].apply(is_true) |
            df['act_mismatch'].apply(is_true) |
            df['jurisdiction_leakage'].apply(is_true) |
            df['unverifiable_dlr_citation'].apply(is_true)
        )
        clean_count = clean_mask.sum()
        pass_rate = (clean_count / total) * 100 if total > 0 else 0

        print(f"Total Questions Evaluated:  {total}")
        print(f"HTTP/Server Errors:         {http500}")
        print(f"Not Found in Knowledge Base:{not_found}")
        print(f"Fabricated Citations:       {fab_cit}")
        print(f"Act Mismatches:             {act_mis}")
        print(f"Jurisdiction Leakage:       {jur_leak}")
        print(f"Unverifiable DLR Citations: {unv_dlr}")
        print("------------------------------------------------")
        print(f"TRUE VERIFIED PASS RATE:    {pass_rate:.2f}% ({clean_count}/{total})")
        print("================================================\n")
        print(f"Full detailed report saved to: {res_file}")

if __name__ == "__main__":
    main()
