import csv
import statistics
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict

flask_releases = {
    "2010-07": "0.2", "2011-06": "0.7", "2011-08": "0.8",
    "2013-05": "0.10", "2014-08": "0.11", "2015-01": "0.10.1",
    "2016-06": "0.11", "2017-05": "0.12", "2018-04": "1.0",
    "2019-05": "1.0.2", "2020-04": "1.1", "2021-05": "2.0",
    "2022-08": "2.2", "2023-04": "2.3", "2023-11": "3.0",
    "2024-08": "3.0.3", "2025-05": "3.1"
}

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

monthly = load_monthly("flask_commits.csv")
months, avgs, mean, std = get_stats(monthly)
threshold = mean + 1.0 * std

# convert months to numeric index for plotting
x = list(range(len(months)))
y = [avgs[m] for m in months]

fig, ax = plt.subplots(figsize=(16, 6))
fig.patch.set_facecolor("#0f0f0f")
ax.set_facecolor("#0f0f0f")

# fill under the entropy line
ax.fill_between(x, y, alpha=0.15, color="#7F77DD")
ax.plot(x, y, color="#7F77DD", linewidth=1.2, label="Monthly avg entropy")

# threshold line
ax.axhline(y=threshold, color="#888", linewidth=0.8,
           linestyle="--", label=f"Spike threshold ({threshold:.1f})")

# highlight spikes
for i, (m, val) in enumerate(zip(months, y)):
    if val > threshold:
        ax.axvspan(i - 0.5, i + 0.5, alpha=0.25, color="#E24B4A")

# release markers
for rel_month, version in flask_releases.items():
    if rel_month in months:
        idx = months.index(rel_month)
        ax.axvline(x=idx, color="#1D9E75", linewidth=1.0,
                   linestyle=":", alpha=0.8)
        ax.text(idx, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else threshold * 2.5,
                version, color="#1D9E75", fontsize=7,
                rotation=90, va="top", ha="right")

# x axis labels — show every 12 months
tick_positions = list(range(0, len(months), 12))
tick_labels = [months[i][:7] for i in tick_positions]
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, rotation=45, ha="right",
                   color="#aaa", fontsize=8)
ax.tick_params(colors="#aaa")

for spine in ax.spines.values():
    spine.set_edgecolor("#333")

ax.set_title("Flask — commit entropy over 15 years",
             color="white", fontsize=14, pad=16)
ax.set_ylabel("Entropy", color="#aaa", fontsize=10)
ax.set_xlabel("Month", color="#aaa", fontsize=10)

spike_patch = mpatches.Patch(color="#E24B4A", alpha=0.4, label="Entropy spike")
release_line = mpatches.Patch(color="#1D9E75", alpha=0.8, label="Major release")
ax.legend(handles=[spike_patch, release_line],
          facecolor="#1a1a1a", edgecolor="#333",
          labelcolor="white", fontsize=9)

plt.tight_layout()
plt.savefig("flask_entropy.png", dpi=150, bbox_inches="tight",
            facecolor="#0f0f0f")
plt.show()
print("Saved to flask_entropy.png")