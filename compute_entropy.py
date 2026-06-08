import pandas as pd
import numpy as np
import json
from scipy.stats import entropy

def shannon_entropy(files_changed):
    counts = files_changed.dropna().astype(int)
    if len(counts) == 0 or counts.sum() == 0:
        return 0
    probs = counts / counts.sum()
    return entropy(probs, base=2)

repos = ['flask', 'django', 'cpython', 'numpy', 'rails', 'rust', 'sklearn', 'react', 'vscode']

with open('data/all_releases_final.json') as f:
    all_releases = json.load(f)

all_data = []

for name in repos:
    print(f"Processing {name}...")
    df = pd.read_csv(f'data/{name}_commits.csv')
    if 'files' in df.columns and 'files_changed' not in df.columns:
        df = df.rename(columns={'files': 'files_changed'})
    df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
    df['month'] = df['date'].dt.to_period('M')

    monthly = df.groupby('month').apply(
        lambda x: pd.Series({
            'entropy': shannon_entropy(x['files_changed']),
            'commit_count': len(x),
            'avg_insertions': x['insertions'].mean(),
            'avg_deletions': x['deletions'].mean(),
        })
    ).reset_index()

    releases = pd.DataFrame(all_releases[name])
    if len(releases) == 0:
        continue
    releases['date'] = pd.to_datetime(releases['date'])
    releases['month'] = releases['date'].dt.to_period('M')
    release_months = set(releases['month'].astype(str))

    monthly['month_str'] = monthly['month'].astype(str)
    monthly['is_release'] = monthly['month_str'].isin(release_months).astype(int)
    # shift label: predict release in next 1-2 months
    monthly['is_release'] = (
        monthly['is_release'] | 
        monthly['is_release'].shift(-1).fillna(0).astype(int) |
        monthly['is_release'].shift(-2).fillna(0).astype(int)
)
    monthly['repo'] = name

    # temporal features
    monthly = monthly.sort_values('month').reset_index(drop=True)
    monthly['entropy_lag1'] = monthly['entropy'].shift(1)
    monthly['entropy_lag2'] = monthly['entropy'].shift(2)
    monthly['entropy_delta'] = monthly['entropy'].diff()
    monthly['commit_delta'] = monthly['commit_count'].diff()
    monthly['churn_ratio'] = monthly['avg_insertions'] / (monthly['avg_insertions'] + monthly['avg_deletions'] + 1e-9)
    monthly['entropy_rolling3'] = monthly['entropy'].rolling(3).mean()

    all_data.append(monthly)
    print(f"  {name}: {len(monthly)} months, {monthly['is_release'].sum()} release months")

combined = pd.concat(all_data, ignore_index=True)
combined.to_csv('data/combined_features.csv', index=False)
print(f"\nSaved combined_features.csv: {len(combined)} rows")