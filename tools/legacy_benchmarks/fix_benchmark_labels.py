import pandas as pd
import re

df = pd.read_csv('brenchmark/justor_benchmark_195.csv')

# Let's inspect rows where question text and expected_act might contradict
corrections = {
    'Q070': ('Trademarks Act, 2009', '24, 26'),
    'Q139': ('Penal Code, 1860', '96'),
    'Q191': ('Partition Act, 1893', '9'),
}

count = 0
for qid, (true_act, true_sec) in corrections.items():
    idx = df[df['id'] == qid].index
    if not idx.empty:
        old_act = df.loc[idx, 'expected_act'].values[0]
        old_sec = df.loc[idx, 'expected_section'].values[0]
        df.loc[idx, 'expected_act'] = true_act
        df.loc[idx, 'expected_section'] = true_sec
        print(f"Corrected {qid}: Act [{old_act} -> {true_act}], Sec [{old_sec} -> {true_sec}]")
        count += 1

df.to_csv('brenchmark/justor_benchmark_195.csv', index=False)
print(f"Saved {count} corrections to brenchmark/justor_benchmark_195.csv")
