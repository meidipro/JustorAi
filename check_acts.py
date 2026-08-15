import pandas as pd
df = pd.read_csv('brenchmark/justor benchmark verified 45.csv')
for q in ['Q01', 'Q02', 'Q04', 'Q18']:
    row = df[df['id']==q].iloc[0]
    print(f"{q}: {row['target_act']} / {row['target_section']}")
