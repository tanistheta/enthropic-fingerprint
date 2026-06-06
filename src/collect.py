from pydriller import Repository
import math
import csv

repo_url = "https://github.com/python/cpython"
output_file = "cpython_commits.csv"

def true_entropy(commit):
    churns = []
    for f in commit.modified_files:
        churn = f.added_lines + f.deleted_lines
        if churn > 0:
            churns.append(churn)
    total = sum(churns)
    if total == 0 or len(churns) < 2:
        return 0.0
    entropy = 0.0
    for c in churns:
        p = c / total
        entropy -= p * math.log2(p)
    return round(entropy * math.log2(total + 1), 4)

rows = []
print("Collecting full Flask history... (this will take 3-5 minutes)")

for i, commit in enumerate(Repository(repo_url, num_workers=1).traverse_commits()):
    churns = [f.added_lines + f.deleted_lines for f in commit.modified_files if f.added_lines + f.deleted_lines > 0]
    total = sum(churns)
    rows.append({
        "hash": commit.hash[:7],
        "date": commit.author_date.date(),
        "year_month": commit.author_date.strftime("%Y-%m"),
        "files": len(churns),
        "insertions": commit.insertions,
        "deletions": commit.deletions,
        "churn": total,
        "entropy": true_entropy(commit),
        "num_authors": 1,
        "msg_len": len(commit.msg)
    })
    if i % 100 == 0:
        print(f"  {i} commits processed...")

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"\nDone. {len(rows)} commits saved to {output_file}")