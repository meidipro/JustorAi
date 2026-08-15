import pandas as pd
import numpy as np

try:
    df = pd.read_csv('brenchmark/benchmark_results_fast.csv')
    
    # Calculate deterministic pass rate
    deterministic_fails = df['fabricated_citation'].fillna(False).astype(bool) | df['act_mismatch'].fillna(False).astype(bool) | df['jurisdiction_leakage'].fillna(False).astype(bool) | df['unverifiable_dlr_citation'].fillna(False).astype(bool)
    deterministic_pass_rate = (1.0 - (deterministic_fails.sum() / len(df))) * 100
    print(f"Deterministic Pass Rate: {deterministic_pass_rate:.2f}% ({len(df) - deterministic_fails.sum()}/{len(df)} passed)")
except Exception as e:
    print('Error:', e)
