import pandas as pd

df = pd.read_csv('brenchmark/benchmark_results_fast_v2.csv')

def is_true(val):
    if isinstance(val, bool): return val
    if isinstance(val, str): return val.strip().lower() == 'true'
    return False

df['fab_cit'] = df['fabricated_citation'].apply(is_true)
df['act_mis'] = df['act_mismatch'].apply(is_true)
df['jur_leak'] = df['jurisdiction_leakage'].apply(is_true)
df['unv_dlr'] = df['unverifiable_dlr_citation'].apply(is_true)

fails = df[df['fab_cit'] | df['act_mis'] | df['jur_leak'] | df['unv_dlr']]
print('Total Rows:', len(df))
print('Fabricated Citation:', df['fab_cit'].sum())
print('Act Mismatch:', df['act_mis'].sum())
print('Jurisdiction Leakage:', df['jur_leak'].sum())
print('Unverifiable DLR:', df['unv_dlr'].sum())

deterministic_pass_rate = (1.0 - (len(fails) / len(df))) * 100
print(f"\nREAL Deterministic Pass Rate: {deterministic_pass_rate:.2f}% ({len(df) - len(fails)}/{len(df)} passed)")

print("\nFAILURES:")
for idx, row in fails.iterrows():
    print(f"Q{row['id']} | Expected: {row['expected_act']}")
    if row['act_mis']: print("  -> Act Mismatch")
    if row['fab_cit']: print(f"  -> Fab Cit: claimed {row['claimed_sections']} but got {row['citations_found']}")
