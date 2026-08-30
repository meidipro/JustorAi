import pandas as pd

df = pd.read_csv("brenchmark/benchmark_results_pilot_launch_v9.csv")

def is_true(val):
    if isinstance(val, bool): return val
    if isinstance(val, (int, float)): return bool(val)
    if isinstance(val, str): return val.strip().lower() == 'true'
    return False

mismatches = df[df['act_mismatch'].apply(is_true)]
print(f"Total Act Mismatches: {len(mismatches)}")
for idx, r in mismatches.iterrows():
    print(f"  {r['id']} ({r['category']}): Expected Act = '{r['expected_act']}' | System Answer excerpt: {str(r['system_answer'])[:120]}...")

print("\nChecking rows with 500/503/errors:")
errs = df[df['system_answer'].str.contains('500|503|Internal Server|error|not locate', case=False, na=False)]
print(f"Total error/not-locate rows: {len(errs)}")
for idx, r in errs.iterrows():
    print(f"  {r['id']}: {str(r['system_answer'])[:100]}...")
