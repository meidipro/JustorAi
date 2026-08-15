import pandas as pd

df = pd.read_csv("brenchmark/benchmark_results_pilot_launch_v9.csv")
for qid in ["Q04", "Q13", "Q24", "Q29", "Q38", "Q42", "Q47", "Q53"]:
    row = df[df['id'] == qid]
    if not row.empty:
        r = row.iloc[0]
        print(f"=== {qid} ({r['category']}) ===")
        print("Expected Act:", r['expected_act'])
        ans = str(r['system_answer'])
        idx = ans.find("---")
        if idx != -1:
            print("Sources:\n", ans[idx:])
        else:
            print("Answer excerpt:", ans[:300])
