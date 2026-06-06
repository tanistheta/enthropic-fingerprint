import csv
import statistics
from collections import defaultdict
from django_releases import django_releases

monthly = defaultdict(list)

with open("django_commits.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        monthly[row["year_month"]].append(float(row["entropy"]))

months = sorted(monthly.keys())
avgs = {m: statistics.mean(monthly[m]) for m in months}
global_mean = statistics.mean(avgs.values())
global_std = statistics.stdev(avgs.values())
threshold = global_mean + 1.0 * global_std

release_months = sorted(django_releases.keys())

print(f"Global mean: {global_mean:.4f}  Std: {global_std:.4f}  Threshold: {threshold:.4f}\n")

early_hits, early_total = 0, 0
modern_hits, modern_total = 0, 0

print(f"{'Version':<10} {'Month':<12} {'Window Max':>12}  Result")
print("-" * 50)

for rel_month in release_months:
    if rel_month not in months:
        continue
    idx = months.index(rel_month)
    window = months[max(0, idx-3):idx+1]
    window_max = max(avgs.get(m, 0) for m in window)
    hit = window_max > threshold
    version = django_releases[rel_month]
    era = "early" if version in ["1.0-pre", "1.0", "1.1", "1.2", "1.3", "1.4"] else "modern"

    print(f"{version:<10} {rel_month:<12} {window_max:>12.4f}  {'HIT' if hit else 'miss'}  [{era}]")

    if era == "early":
        early_total += 1
        if hit: early_hits += 1
    else:
        modern_total += 1
        if hit: modern_hits += 1

print(f"\nEarly era:   {early_hits}/{early_total} = {early_hits/early_total*100:.0f}%")
print(f"Modern era:  {modern_hits}/{modern_total} = {modern_hits/modern_total*100:.0f}%")