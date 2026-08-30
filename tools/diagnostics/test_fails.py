import pandas as pd
df = pd.read_csv('D:/Justor AI/JustorAi/brenchmark/benchmark_results_local_50_100.csv')
for _, row in df.iterrows():
    if row['has_expected_section'] and not row['expected_section_mentioned']:
        print(f"Q{row['question_id']}: {row['expected_act']} - {row['expected_section']} | Cited: {row['sections_cited']}")
