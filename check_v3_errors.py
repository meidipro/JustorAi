import pandas as pd
df = pd.read_csv('brenchmark/benchmark_results_fast_v3.csv')
for idx, row in df[df['id'].isin([38, 39, 40, 41, 42, 44, 45, 46, 47, 48])].iterrows():
    print(f"Q{row['id']}: status={row['status_code']} | ans={row['actual_answer'][:100]}...")
