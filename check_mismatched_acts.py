import pandas as pd
df = pd.read_csv('brenchmark/benchmark_results_fast_v8.csv')
flagged = df[df['id'].isin(['Q38', 'Q42', 'Q45', 'Q47', 'Q53'])]
for _, row in flagged.iterrows():
    print(f"{row['id']} | Expected: {row['expected_act']} | Got: {row['other_acts_mentioned']}")
