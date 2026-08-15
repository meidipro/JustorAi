import pandas as pd
import numpy as np

try:
    df = pd.read_csv('brenchmark/benchmark_results.csv')
    
    # Calculate deterministic pass rate
    deterministic_fails = df['fabricated_citation'].fillna(False).astype(bool) | df['act_mismatch'].fillna(False).astype(bool) | df['jurisdiction_leakage'].fillna(False).astype(bool) | df['unverifiable_dlr_citation'].fillna(False).astype(bool)
    deterministic_pass_rate = (1.0 - (deterministic_fails.sum() / len(df))) * 100
    print(f"Deterministic Pass Rate: {deterministic_pass_rate:.2f}% ({len(df) - deterministic_fails.sum()}/{len(df)} passed)")
    
    # RAGAS metrics
    for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
        if metric in df.columns:
            # convert to numeric, coercing errors like 'NOT_AVAILABLE' to NaN
            vals = pd.to_numeric(df[metric], errors='coerce')
            valid_vals = vals.dropna()
            if len(valid_vals) > 0:
                avg = valid_vals.mean() * 100
                print(f"RAGAS {metric.replace('_', ' ').title()}: {avg:.2f}% (over {len(valid_vals)} valid rows)")
            else:
                print(f"RAGAS {metric}: No valid scores")
except Exception as e:
    print('Error:', e)
