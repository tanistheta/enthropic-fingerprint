import requests
import json

TOKEN = "your_github_token_here"
HEADERS = {"Authorization": f"token {TOKEN}"}

repos = {
    'django':  'django/django',
    'cpython': 'python/cpython',
}

for name, repo in repos.items():
    print(f"Fetching tags for {name}...")
    releases = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/tags?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        tags = r.json()
        if not tags or 'message' in tags:
            break
        for tag in tags:
            # get commit date for this tag
            commit_url = tag['commit']['url']
            cr = requests.get(commit_url, headers=HEADERS)
            cd = cr.json()
            date = cd['commit']['committer']['date'][:10]
            if '2018-01-01' <= date <= '2024-12-31':
                releases.append({
                    'version': tag['name'],
                    'date': date
                })
        if len(tags) < 100:
            break
        page += 1

    print(f"  {name}: {len(releases)} releases found")

    # merge into existing all_releases.json
    with open('data/all_releases.json', 'r') as f:
        all_releases = json.load(f)
    all_releases[name] = releases
    with open('data/all_releases.json', 'w') as f:
        json.dump(all_releases, f, indent=2)

print("Done")