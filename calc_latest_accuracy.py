import pandas as pd

df = pd.read_csv('brenchmark/benchmark_results_latest.csv')
total = len(df)

def is_answered(ans):
    if not isinstance(ans, str) or not ans.strip():
        return False
    refusal_phrases = ["not in my verified database", "no verified sources found", "cannot verify"]
    return not any(p in ans.lower() for p in refusal_phrases)

def is_true(val):
    if isinstance(val, bool): return val
    if isinstance(val, (int, float)): return bool(val)
    if isinstance(val, str): return val.strip().lower() == 'true'
    return False

df['answered'] = df['system_answer'].apply(is_answered)
df['sec_acc'] = df['expected_section_mentioned'].apply(is_true)
df['fab_cit'] = df['fabricated_citation'].apply(is_true)
df['act_mis'] = df['act_mismatch'].apply(is_true)
df['jur_leak'] = df['jurisdiction_leakage'].apply(is_true)
df['unv_dlr'] = df['unverifiable_dlr_citation'].apply(is_true)

answered_df = df[df['answered']]
clean_answered = answered_df[~(answered_df['fab_cit'] | answered_df['act_mis'] | answered_df['jur_leak'] | answered_df['unv_dlr'])]

print("TOTAL:", total)
print("COVERAGE (Answered):", len(answered_df), f"({len(answered_df)/total*100:.1f}%)")
print("SECTION ACCURACY (Overall):", df['sec_acc'].sum(), f"({df['sec_acc'].mean()*100:.1f}%)")
print("SECTION ACCURACY (Among Answered):", answered_df['sec_acc'].sum(), f"({answered_df['sec_acc'].mean()*100:.1f}%)")
print("ACT ACCURACY (Correct Act, No Mismatch):", (total - df['act_mis'].sum()), f"({(1 - df['act_mis'].mean())*100:.1f}%)")
print("TRUE PASS RATE (Answered & Zero Errors/Hallucinations):", len(clean_answered), f"({len(clean_answered)/total*100:.1f}%)")
