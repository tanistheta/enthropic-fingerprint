import requests
import json
from datetime import datetime

TOKEN = "your_github_token_here"  # paste your token here
HEADERS = {"Authorization": f"token {TOKEN}"}

repos = {
    'flask':   'pallets/flask',
    'django':  'django/django',
    'cpython': 'python/cpython',
    'numpy':   'numpy/numpy',
    'rails':   'rails/rails',
    'rust':    'rust-lang/rust',
    'sklearn': 'scikit-learn/scikit-learn',
    'react':   'facebook/react',
    'vscode':  'microsoft/vscode',
}

all_releases = {}

for name, repo in repos.items():
    print(f"Fetching releases for {name}...")
    releases = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        if not data or 'message' in data:
            break
        for rel in data:
            date = rel['published_at'][:10]  # YYYY-MM-DD
            if '2018-01-01' <= date <= '2024-12-31':
                releases.append({
                    'version': rel['tag_name'],
                    'date': date
                })
        if len(data) < 100:
            break
        page += 1
    all_releases[name] = releases
    print(f"  {name}: {len(releases)} releases found")

with open('data/all_releases.json', 'w') as f:
    json.dump(all_releases, f, indent=2)

print("Saved to data/all_releases.json")