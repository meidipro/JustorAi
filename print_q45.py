import pandas as pd
df = pd.read_csv('brenchmark/benchmark_results_fast.csv')
q45 = df[df['id'] == 'Q45'].iloc[0]
with open('q45_answer.txt', 'w', encoding='utf-8') as f:
    f.write(q45['system_answer'])
