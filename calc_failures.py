import pandas as pd
df = pd.read_csv('brenchmark/benchmark_results_fast.csv')

print('Total Rows:', len(df))
print('Fabricated Citation (True):', df['fabricated_citation'].fillna(False).astype(bool).sum())
print('Act Mismatch (True):', df['act_mismatch'].fillna(False).astype(bool).sum())
print('Jurisdiction Leakage (True):', df['jurisdiction_leakage'].fillna(False).astype(bool).sum())
print('Unverifiable DLR (True):', df['unverifiable_dlr_citation'].fillna(False).astype(bool).sum())

# Let's see some failed rows
print('\nSample Failures:')
failures = df[df['fabricated_citation'].fillna(False).astype(bool) | df['act_mismatch'].fillna(False).astype(bool)]
for _, row in failures.head(3).iterrows():
    print(f"Q: {row['question'][:50]}... | ACT: {row['expected_act']} | SEC: {row['expected_section']}")
    print(f"System Answer: {row['system_answer'][:150]}...")
    print(f"Citations Found: {row['citations_found']}")
    print(f"Claimed Sections: {row['claimed_sections']}")
    print('---')
