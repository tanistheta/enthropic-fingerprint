import csv
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict
from django_releases import django_releases as dj_releases

def load_monthly(filepath):
    monthly = defaultdict(list)
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            monthly[row["year_month"]].append(float(row["entropy"]))
    return monthly

def get_stats(monthly):
    months = sorted(monthly.keys())
    avgs = {m: statistics.mean(monthly[m]) for m in months}
    all_avgs = list(avgs.values())
    mean = statistics.mean(all_avgs)
    std = statistics.stdev(all_avgs)
    return months, avgs, mean, std

monthly2 = load_monthly("django_commits.csv")
months2, avgs2, mean2, std2 = get_stats(monthly2)
threshold2 = mean2 + 1.0 * std2

x2 = list(range(len(months2)))
y2 = [avgs2[m] for m in months2]

fig, ax = plt.subplots(figsize=(16, 6))
fig.patch.set_facecolor("#0f0f0f")
ax.set_facecolor("#0f0f0f")

ax.fill_between(x2, y2, alpha=0.15, color="#1D9E75")
ax.plot(x2, y2, color="#1D9E75", linewidth=1.2)
ax.axhline(y=threshold2, color="#888", linewidth=0.8, linestyle="--")

for i, (m, val) in enumerate(zip(months2, y2)):
    if val > threshold2:
        ax.axvspan(i - 0.5, i + 0.5, alpha=0.25, color="#E24B4A")

for rel_month, version in dj_releases.items():
    if rel_month in months2:
        idx = months2.index(rel_month)
        ax.axvline(x=idx, color="#7F77DD", linewidth=1.0, linestyle=":", alpha=0.8)
        ax.text(idx, max(y2) * 0.95, version, color="#7F77DD",
                fontsize=7, rotation=90, va="top", ha="right")

tick_positions = list(range(0, len(months2), 12))
tick_labels = [months2[i][:7] for i in tick_positions]
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, rotation=45, ha="right", color="#aaa", fontsize=8)
ax.tick_params(colors="#aaa")
for spine in ax.spines.values():
    spine.set_edgecolor("#333")

ax.set_title("Django — commit entropy over 20 years", color="white", fontsize=14, pad=16)
ax.set_ylabel("Entropy", color="#aaa", fontsize=10)
ax.set_xlabel("Month", color="#aaa", fontsize=10)

plt.tight_layout()
plt.savefig("django_entropy.png", dpi=150, bbox_inches="tight", facecolor="#0f0f0f")
plt.show()
print("Saved to django_entropy.png")