import csv
import statistics
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import classification_report
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
    mean = statistics.mean(avgs.values())
    std = statistics.stdev(avgs.values())
    return months, avgs, mean, std

def build_features(filepath, releases):
    monthly = load_monthly(filepath)
    months, avgs, mean, std = get_stats(monthly)
    threshold = mean + 1.0 * std
    release_set = set(releases.keys())

    rows = []
    for i in range(4, len(months)):
        m = months[i]

        # features: rolling entropy window
        e0 = avgs[months[i]]
        e1 = avgs[months[i-1]]
        e2 = avgs[months[i-2]]
        e3 = avgs[months[i-3]]

        rolling_mean = (e0 + e1 + e2 + e3) / 4
        rolling_max  = max(e0, e1, e2, e3)
        trend        = e0 - e3
        spike_count  = sum(1 for e in [e0,e1,e2,e3] if e > threshold)
        z_score      = (e0 - mean) / std if std > 0 else 0

        # label: is there a release in next 3 months?
        future = months[i+1:i+4] if i+4 <= len(months) else months[i+1:]
        label = 1 if any(f in release_set for f in future) else 0

        rows.append({
            "month": m,
            "e0": e0, "e1": e1, "e2": e2, "e3": e3,
            "rolling_mean": rolling_mean,
            "rolling_max": rolling_max,
            "trend": trend,
            "spike_count": spike_count,
            "z_score": z_score,
            "label": label
        })
    return pd.DataFrame(rows)

print("Building features...")
flask_df  = build_features("flask_commits.csv",   flask_releases)
django_df = build_features("django_commits.csv",  dj_releases)

flask_df["repo"]  = "flask"
django_df["repo"] = "django"

# train on django, test on flask — and vice versa
feature_cols = ["rolling_mean", "rolling_max", "trend", "spike_count", "z_score"]

print("\n=== PROBABILITY-BASED EVALUATION ===")
print("Train: Django  |  Test: Flask\n")

clf1 = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
clf1.fit(django_df[feature_cols], django_df["label"])

flask_df["release_prob"] = clf1.predict_proba(flask_df[feature_cols])[:, 1]

# sort by probability and check — do high prob months precede releases?
high_risk = flask_df[flask_df["release_prob"] > 0.4].copy()
low_risk  = flask_df[flask_df["release_prob"] <= 0.4].copy()

high_release_rate = high_risk["label"].mean()
low_release_rate  = low_risk["label"].mean()

print(f"High risk months (prob > 0.4): {len(high_risk)} months")
print(f"  Release rate in high risk:   {high_release_rate:.1%}")
print(f"Low risk months (prob <= 0.4): {len(low_risk)} months")
print(f"  Release rate in low risk:    {low_release_rate:.1%}")
print(f"  Lift: {high_release_rate/low_release_rate:.1f}x more likely to precede a release")

print("\nTop 10 highest risk months Flask (model never saw):")
print(flask_df[["month", "release_prob", "label"]]
      .sort_values("release_prob", ascending=False)
      .head(10)
      .to_string(index=False))

print("\n=== FEATURE IMPORTANCE ===")
for feat, imp in sorted(zip(feature_cols, clf1.feature_importances_),
                         key=lambda x: -x[1]):
    bar = "#" * int(imp * 40)
    print(f"  {feat:<20} {imp:.4f}  {bar}")