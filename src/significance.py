import csv
import statistics
import random
from collections import defaultdict
from django_releases import django_releases as dj_releases

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
    mean = statistics.mean(avgs.values())
    std = statistics.stdev(avgs.values())
    return months, avgs, mean, std

def compute_accuracy(months, avgs, release_set, mean, std, window=3):
    threshold = mean + 1.0 * std
    early_versions = ["0.2","0.7","0.8","0.10","0.11","0.10.1",
                      "1.0-pre","1.0","1.1","1.2","1.3","1.4",
                      "2.0","2.1","2.2","2.3","2.4","2.5",
                      "2.6","2.7","3.0","3.1","3.2"]
    hits, total = 0, 0
    for rel_month in release_set:
        if rel_month not in months:
            continue
        idx = months.index(rel_month)
        if idx < window:
            continue
        win = months[max(0, idx-window):idx+1]
        window_max = max(avgs.get(m, 0) for m in win)
        hits += 1 if window_max > threshold else 0
        total += 1
    return hits / total if total > 0 else 0

def permutation_test(months, avgs, release_months, mean, std, n=10000):
    # observed accuracy
    observed = compute_accuracy(months, avgs,
                                set(release_months), mean, std)

    # shuffle release dates randomly n times
    # keep same number of releases, just place them randomly
    all_months = list(months)
    n_releases = len([r for r in release_months if r in months])
    
    null_distribution = []
    for _ in range(n):
        fake_releases = set(random.sample(all_months, n_releases))
        acc = compute_accuracy(months, avgs, fake_releases, mean, std)
        null_distribution.append(acc)

    # p-value: fraction of random shuffles that beat observed accuracy
    p_value = sum(1 for x in null_distribution if x >= observed) / n
    null_mean = statistics.mean(null_distribution)
    null_std = statistics.stdev(null_distribution)
    z = (observed - null_mean) / null_std

    return observed, p_value, null_mean, null_std, z

random.seed(42)

print("Running permutation tests (10,000 iterations each)...\n")

# Flask
flask_monthly = load_monthly("flask_commits.csv")
flask_months, flask_avgs, flask_mean, flask_std = get_stats(flask_monthly)
flask_rel_months = [m for m in flask_releases.keys() if m in flask_months]

obs, p, nm, ns, z = permutation_test(
    flask_months, flask_avgs, flask_rel_months, flask_mean, flask_std)
print(f"Flask")
print(f"  Observed accuracy:     {obs:.1%}")
print(f"  Null mean accuracy:    {nm:.1%}")
print(f"  Z-score:               {z:.2f}")
print(f"  p-value:               {p:.4f}  {'*** SIGNIFICANT ***' if p < 0.05 else '(not significant)'}")

# Django
dj_monthly = load_monthly("django_commits.csv")
dj_months, dj_avgs, dj_mean, dj_std = get_stats(dj_monthly)
dj_rel_months = [m for m in dj_releases.keys() if m in dj_months]

obs2, p2, nm2, ns2, z2 = permutation_test(
    dj_months, dj_avgs, dj_rel_months, dj_mean, dj_std)
print(f"\nDjango")
print(f"  Observed accuracy:     {obs2:.1%}")
print(f"  Null mean accuracy:    {nm2:.1%}")
print(f"  Z-score:               {z2:.2f}")
print(f"  p-value:               {p2:.4f}  {'*** SIGNIFICANT ***' if p2 < 0.05 else '(not significant)'}")

print(f"\n=== COMBINED ===")
print(f"  Flask p={p:.4f}, Django p={p2:.4f}")
if p < 0.05 and p2 < 0.05:
    print(f"  Both significant at p<0.05 -- the finding is not due to chance.")
elif p < 0.05 or p2 < 0.05:
    print(f"  One significant -- partial evidence.")
else:
    print(f"  Neither significant -- finding may be due to chance.")