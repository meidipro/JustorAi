import pandas as pd

df = pd.read_csv('brenchmark/benchmark_results_fast.csv')

def is_true(val):
    if isinstance(val, bool): return val
    if isinstance(val, str): return val.strip().lower() == 'true'
    return False

df['fab_cit'] = df['fabricated_citation'].apply(is_true)
df['act_mis'] = df['act_mismatch'].apply(is_true)
df['jur_leak'] = df['jurisdiction_leakage'].apply(is_true)
df['unv_dlr'] = df['unverifiable_dlr_citation'].apply(is_true)

fails = df[df['fab_cit'] | df['act_mis'] | df['jur_leak'] | df['unv_dlr']]
print(f"Total fails: {len(fails)}")
for idx, row in fails.iterrows():
    print(f"Q{row['id']}: {row['question'][:60]}... | Expected: {row['expected_act']}")
    if row['act_mis']: print("  -> Act Mismatch")
    if row['fab_cit']: print(f"  -> Fab Cit: claimed {row['claimed_sections']} but got {row['citations_found']}")
    print("---")
