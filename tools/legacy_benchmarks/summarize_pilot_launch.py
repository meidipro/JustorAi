import pandas as pd
import os

df = pd.read_csv("brenchmark/benchmark_results_latest.csv")
total = len(df)

# An answered question is one where system_answer does not say "verified database" refusal
def is_answered(ans):
    if not isinstance(ans, str) or not ans.strip():
        return False
    refusal_phrases = ["not in my verified database", "no verified sources found", "cannot verify"]
    return not any(p in ans.lower() for p in refusal_phrases)

df['answered'] = df['system_answer'].apply(is_answered)
answered_count = df['answered'].sum()
coverage = (answered_count / total) * 100

sec_acc = df['expected_section_mentioned'].mean() * 100
fab_rate = df['fabricated_citation'].mean() * 100
leak_rate = df['jurisdiction_leakage'].mean() * 100
act_mismatch_rate = df['act_mismatch'].mean() * 100

print("==========================================")
print("       JUSTOR AI PILOT LAUNCH SCORECARD   ")
print("==========================================")
print(f"Total Questions:         {total}")
print(f"Coverage (Answered):     {answered_count}/{total} ({coverage:.1f}%)")
print(f"Section Accuracy:        {sec_acc:.1f}%")
print(f"Act Mismatch Rate:       {act_mismatch_rate:.1f}%")
print(f"Fabricated Citations:    {fab_rate:.1f}%")
print(f"Jurisdiction Leakage:    {leak_rate:.1f}%")
print("==========================================")

print("\nQ04 Full System Answer:")
print(df[df['id'] == 'Q04']['system_answer'].iloc[0][:1500])


