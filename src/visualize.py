import csv
from collections import defaultdict
import statistics

input_file = "flask_commits.csv"

monthly = defaultdict(list)

with open(input_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        monthly[row["year_month"]].append(float(row["entropy"]))

print(f"{'Month':<12} {'Commits':>8} {'Avg Entropy':>13} {'Max Entropy':>13}  Sparkline")
print("-" * 70)

max_avg = max(statistics.mean(v) for v in monthly.values())

for month in sorted(monthly.keys()):
    values = monthly[month]
    avg = statistics.mean(values)
    mx = max(values)
    commits = len(values)
    
    # sparkline bar scaled to terminal width
    bar_len = int((avg / max_avg) * 30)
    bar = "█" * bar_len + "░" * (30 - bar_len)
    
    print(f"{month:<12} {commits:>8} {avg:>13.4f} {mx:>13.4f}  {bar}")