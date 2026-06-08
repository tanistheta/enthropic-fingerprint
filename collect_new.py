import pandas as pd
from pydriller import Repository
from datetime import datetime

DATE_FROM = datetime(2018, 1, 1)
DATE_TO = datetime(2024, 12, 31)

# --- Trim existing ---
for repo in ['flask', 'django', 'cpython']:
    df = pd.read_csv(f'data/{repo}_commits.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= DATE_FROM) & (df['date'] <= DATE_TO)]
    df.to_csv(f'data/{repo}_commits.csv', index=False)
    print(f"{repo}: trimmed to {len(df)} commits")

# --- Collect new repos ---
new_repos = {
    'numpy':      'https://github.com/numpy/numpy',
    #'linux':      'https://github.com/torvalds/linux',
    'rails':      'https://github.com/rails/rails',
    'rust':       'https://github.com/rust-lang/rust',
    'tensorflow': 'https://github.com/tensorflow/tensorflow',
    'react':      'https://github.com/facebook/react',
    'vscode':     'https://github.com/microsoft/vscode',
}

for name, url in new_repos.items():
    print(f"Collecting {name}...")
    records = []
    for commit in Repository(url, since=DATE_FROM, to=DATE_TO).traverse_commits():
        records.append({
            'hash': commit.hash,
            'date': commit.committer_date,
            'files_changed': commit.files,
            'insertions': commit.insertions,
            'deletions': commit.deletions,
        })
    df = pd.DataFrame(records)
    df.to_csv(f'data/{name}_commits.csv', index=False)
    print(f"{name}: {len(df)} commits saved")