import os

# Let's check backend_benchmark.log
with open("backend_benchmark.log", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("Total lines in backend_benchmark.log:", len(lines))
print("Last 10 lines:")
for line in lines[-10:]:
    print(" ", line.strip())
