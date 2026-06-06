from pydriller import Repository
import math

repo_url = "https://github.com/pallets/flask"

def true_entropy(commit):
    churns = []
    for f in commit.modified_files:
        churn = f.added_lines + f.deleted_lines
        if churn > 0:
            churns.append(churn)
    
    total = sum(churns)
    if total == 0 or len(churns) < 2:
        return 0.0
    
    # real Shannon entropy over file-level churn distribution
    entropy = 0.0
    for c in churns:
        p = c / total
        entropy -= p * math.log2(p)
    
    # scale by log of total churn so bigger commits aren't penalized
    return round(entropy * math.log2(total + 1), 4)

print(f"{'Hash':<10} {'Date':<12} {'Files':>6} {'Churn':>8} {'Entropy':>10}  Distribution")
print("-" * 75)

for i, commit in enumerate(Repository(repo_url, num_workers=1).traverse_commits()):
    churns = [f.added_lines + f.deleted_lines for f in commit.modified_files if f.added_lines + f.deleted_lines > 0]
    total = sum(churns)
    e = true_entropy(commit)
    
    # show how churn is distributed across files
    if len(churns) > 1:
        dist = " | ".join([str(c) for c in sorted(churns, reverse=True)[:5]])
        if len(churns) > 5:
            dist += f" ... (+{len(churns)-5} more)"
    else:
        dist = str(churns[0]) if churns else "0"
    
    print(f"{commit.hash[:7]:<10} {str(commit.author_date.date()):<12} {len(churns):>6} {total:>8} {e:>10}  [{dist}]")
    
    if i >= 29:
        break