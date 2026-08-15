import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_csv('brenchmark/benchmark_results_fast_v7.csv')

http500 = df['system_answer'].str.contains('500|Internal Server Error|HTTPError', case=False, na=False)
not_found = df['system_answer'].str.contains('not locate|not in my verified|error|503', case=False, na=False)
all_errors = http500 | not_found

print(f"Total: {len(df)}")
print(f"HTTP 500 errors: {http500.sum()}")
print(f"Not found: {not_found.sum()}")
print(f"Total failures: {all_errors.sum()}")
print(f"Real answers: {(~all_errors).sum()}")

def is_true(val):
    if isinstance(val, bool): return val
    if isinstance(val, str): return val.strip().lower() == 'true'
    return False

df['fab_cit'] = df['fabricated_citation'].apply(is_true)
df['act_mis'] = df['act_mismatch'].apply(is_true)
df['jur_leak'] = df['jurisdiction_leakage'].apply(is_true)
df['unv_dlr'] = df['unverifiable_dlr_citation'].apply(is_true)

answered = df[~all_errors]
clean = answered[~(answered['fab_cit'] | answered['act_mis'] | answered['jur_leak'] | answered['unv_dlr'])]
pass_rate = len(clean) / len(df) * 100
print(f"\nTrue Pass Rate: {pass_rate:.2f}% ({len(clean)}/{len(df)})")

print("\n=== ALL ROWS ===")
for idx, row in df.iterrows():
    ans = str(row['system_answer'])[:100]
    err = "500" if http500[idx] else ("NF" if not_found[idx] else "OK")
    print(f"  [{err}] {row['id']} | {ans}")
