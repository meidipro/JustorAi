import pandas as pd
df = pd.read_csv('brenchmark/benchmark_results_fast_v7.csv')
flagged = df[(df['fabricated_citation']==True) | (df['act_mismatch']==True) | (df['jurisdiction_leakage']==True) | (df['unverifiable_dlr_citation']==True)]
for _, row in flagged.iterrows():
    print(f"{row['id']} | Fab:{row['fabricated_citation']} | Mismatch:{row['act_mismatch']} | Leak:{row['jurisdiction_leakage']}")
