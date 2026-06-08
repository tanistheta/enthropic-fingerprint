from pydriller import Repository
from datetime import datetime
import pandas as pd

DATE_FROM = datetime(2018, 1, 1)
DATE_TO = datetime(2024, 12, 31)

repos = {
    'sklearn':  'https://github.com/scikit-learn/scikit-learn',
    'react':    'https://github.com/facebook/react',
    'vscode':   'https://github.com/microsoft/vscode',
}

for name, url in repos.items():
    print(f"Collecting {name}...")
    records = []
    for commit in Repository(url, since=DATE_FROM, to=DATE_TO).traverse_commits():
        try:
            records.append({
                'hash': commit.hash,
                'date': commit.committer_date,
                'files_changed': commit.files,
                'insertions': commit.insertions,
                'deletions': commit.deletions,
            })
        except Exception:
            records.append({
                'hash': commit.hash,
                'date': commit.committer_date,
                'files_changed': None,
                'insertions': None,
                'deletions': None,
            })
    df = pd.DataFrame(records)
    df.to_csv(f'data/{name}_commits.csv', index=False)
    print(f"{name}: {len(df)} commits saved")