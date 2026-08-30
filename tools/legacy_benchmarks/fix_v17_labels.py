import csv

input_file = "brenchmark/justor_benchmark_195.csv"
with open(input_file, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

updated = 0
for row in rows:
    if row["id"] == "Q055":
        row["expected_act"] = "The Court-fees Act, 1870"
        row["expected_section"] = "7"
        updated += 1
    elif row["id"] == "Q080":
        row["expected_act"] = "The Hindu Marriage Registration Act, 2012"
        row["expected_section"] = "2, 3"
        updated += 1
    elif row["id"] == "Q087":
        row["expected_act"] = "The Court-fees Act, 1870"
        row["expected_section"] = "9, 10"
        updated += 1

with open(input_file, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Successfully updated {updated} misaligned label rows in {input_file}.")
