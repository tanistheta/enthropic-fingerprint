import csv
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict
from django_releases import django_releases as dj_releases
from cpython_releases import cpython_releases as cp_releases

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

repos = [
    ("flask_commits.csv",   flask_releases, "#7F77DD", "Flask — 5,539 commits — irregular releases — 70% accuracy"),
    ("django_commits.csv",  dj_releases,    "#1D9E75", "Django — 34,665 commits — irregular releases — 74% accuracy"),
    ("cpython_commits.csv", cp_releases,    "#EF9F27", "CPython — 131,677 commits — annual release cycle — 36% accuracy"),
]

fig, axes = plt.subplots(3, 1, figsize=(18, 14))
fig.patch.set_facecolor("#0f0f0f")
fig.suptitle("Entropic Fingerprint — commit entropy as a predictor of major releases",
             color="white", fontsize=15, y=0.98)

for ax, (filepath, releases, color, title) in zip(axes, repos):
    monthly = load_monthly(filepath)
    months, avgs, mean, std = get_stats(monthly)
    threshold = mean + 1.0 * std

    x = list(range(len(months)))
    y = [avgs[m] for m in months]

    ax.set_facecolor("#0f0f0f")
    ax.fill_between(x, y, alpha=0.15, color=color)
    ax.plot(x, y, color=color, linewidth=1.0)
    ax.axhline(y=threshold, color="#555", linewidth=0.7, linestyle="--")

    for i, (m, val) in enumerate(zip(months, y)):
        if val > threshold:
            ax.axvspan(i - 0.5, i + 0.5, alpha=0.2, color="#E24B4A")

    for rel_month, version in releases.items():
        if rel_month in months:
            idx = months.index(rel_month)
            ax.axvline(x=idx, color="white", linewidth=0.6,
                       linestyle=":", alpha=0.5)

    tick_positions = list(range(0, len(months), 12))
    tick_labels = [months[i][:7] for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right",
                       color="#888", fontsize=7)
    ax.tick_params(colors="#888")
    for spine in ax.spines.values():
        spine.set_edgecolor("#222")

    ax.set_title(title, color=color, fontsize=11, pad=8)
    ax.set_ylabel("Entropy", color="#888", fontsize=9)

# bottom annotation
fig.text(0.5, 0.01,
         "Red = entropy spike  |  White dotted = major release  |  Signal holds in irregular cycles (72%), disappears in annual cycles (36%)",
         ha="center", color="#666", fontsize=9)

plt.tight_layout(rect=[0, 0.02, 1, 0.97])
plt.savefig("entropic_fingerprint.png", dpi=150,
            bbox_inches="tight", facecolor="#0f0f0f")
plt.show()
print("Saved to entropic_fingerprint.png")