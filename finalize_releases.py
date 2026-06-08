import json
import re

with open('data/all_releases_filtered.json') as f:
    releases = json.load(f)

for name in ['django', 'cpython', 'numpy']:
    before = len(releases[name])
    max_patch = 1 if name == 'numpy' else 2
    filtered = []
    for r in releases[name]:
        v = re.sub(r'^v', '', r['version'])
        parts = v.split('.')
        if len(parts) >= 2:
            try:
                patch = int(parts[2]) if len(parts) >= 3 else 0
                if patch <= max_patch:
                    filtered.append(r)
            except ValueError:
                pass
    releases[name] = filtered
    months = len(set(r['date'][:7] for r in releases[name]))
    print(f"{name}: {before} -> {len(releases[name])} releases, {months} unique months")

print()
for name, rels in releases.items():
    months = len(set(r['date'][:7] for r in rels))
    print(f"{name}: {len(rels)} releases, {months} unique release months / 84 total")

with open('data/all_releases_final.json', 'w') as f:
    json.dump(releases, f, indent=2)

print("\nSaved all_releases_final.json")