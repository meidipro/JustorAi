import pandas as pd

df = pd.read_csv('brenchmark/benchmark_results_fast_v5.csv')

def is_true(val):
    if isinstance(val, bool): return val
    if isinstance(val, str): return val.strip().lower() == 'true'
    return False

df['fab_cit'] = df['fabricated_citation'].apply(is_true)
df['act_mis'] = df['act_mismatch'].apply(is_true)
df['jur_leak'] = df['jurisdiction_leakage'].apply(is_true)
df['unv_dlr'] = df['unverifiable_dlr_citation'].apply(is_true)

# Server errors = system_answer contains "not in my verified database" or "error"
not_found = df['system_answer'].str.contains('not locate|not in my verified|error|503', case=False, na=False)
errors = df[not_found]
answered = df[~not_found]

print(f'Total: {len(df)}')
print(f'Not found / server errors: {len(errors)}')
print(f'Answered: {len(answered)}')
print(f'Fabricated Citation: {df["fab_cit"].sum()}')
print(f'Act Mismatch:        {df["act_mis"].sum()}')
print(f'Jurisdiction Leak:   {df["jur_leak"].sum()}')
print(f'Unverifiable DLR:    {df["unv_dlr"].sum()}')

clean = answered[~(answered['fab_cit'] | answered['act_mis'] | answered['jur_leak'] | answered['unv_dlr'])]
pass_rate = len(clean) / len(df) * 100
print(f'\nDeterministic Pass Rate: {pass_rate:.2f}% ({len(clean)}/{len(df)})')

print('\n=== SEMANTIC FAILURES ===')
sem_fails = df[df['fab_cit'] | df['act_mis'] | df['jur_leak'] | df['unv_dlr']]
for idx, row in sem_fails.iterrows():
    reasons = []
    if row['act_mis']: reasons.append('ActMismatch')
    if row['fab_cit']: reasons.append('FabCit')
    if row['jur_leak']: reasons.append('JurLeak')
    if row['unv_dlr']: reasons.append('UnvDLR')
    print(f"  {row['id']} | {row['expected_act']} | {' + '.join(reasons)}")

print('\n=== NOT FOUND (retrieval miss / server error) ===')
for idx, row in errors.iterrows():
    print(f"  {row['id']} | Expected: {row['expected_act']}")
