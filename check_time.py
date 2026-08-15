import os, time
from datetime import datetime

for root, dirs, files in os.walk('brenchmark'):
    for f in files:
        if f.endswith('.csv'):
            path = os.path.join(root, f)
            mtime = os.path.getmtime(path)
            dt = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{path}: last modified {dt}")
