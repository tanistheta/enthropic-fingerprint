import csv
import statistics
from collections import defaultdict

# Flask major releases from public changelog
# https://flask.palletsprojects.com/en/stable/changes/
flask_releases = {
    "2010-07": "0.2", "2011-06": "0.7", "2011-08": "0.8",
    "2013-05": "0.10", "2014-08": "0.11", "2015-01": "0.10.1",
    "2016-06": "0.11", "2017-05": "0.12", "2018-04": "1.0",
    "2019-05": "1.0.2", "2020-04": "1.1", "2021-05": "2.0",
    "2022-08": "2.2", "2023-04": "2.3", "2023-11": "3.0",
    "2024-08": "3.0.3", "2025-05": "3.1"
}

monthly = defaultdict(list)

with open("flask_commits.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        monthly[row["year_month"]].append(float(row["entropy"]))

print(f"{'Month':<12} {'Avg Entropy':>12} {'Release':>10}  {'Signal'}")
print("-" * 60)

all_avgs = [statistics.mean(v) for v in monthly.values()]
global_mean = statistics.mean(all_avgs)
global_std = statistics.stdev(all_avgs)

for month in sorted(monthly.keys()):
    values = monthly[month]
    avg = statistics.mean(values)
    release = flask_releases.get(month, "")
    
    # flag months that are > 1 std dev above mean
    z = (avg - global_mean) / global_std
    if z > 1.5:
        signal = "SPIKE"
    elif z > 1.0:
        signal = "elevated"
    else:
        signal = ""
    
    marker = " <-- RELEASE" if release else ""
    if release or signal:
        print(f"{month:<12} {avg:>12.4f} {release:>10}  {signal}{marker}")