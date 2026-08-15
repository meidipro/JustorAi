import shutil
import os
import hashlib
import pandas as pd

src = "brenchmark/benchmark_results_latest.csv"
dst = "brenchmark/benchmark_results_pilot_launch_v9.csv"

shutil.copy2(src, dst)

with open(dst, "rb") as f:
    file_hash = hashlib.md5(f.read()).hexdigest()

df = pd.read_csv(dst)
print(f"Copied {src} -> {dst}")
print(f"File MD5 Hash: {file_hash}")
print(f"Total Rows: {len(df)}")
print(f"Answered Count: {(df['system_answer'].str.contains('verified database') == False).sum()}")
