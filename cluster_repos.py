import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json

df = pd.read_csv('data/combined_features.csv')

# compute per-repo entropy profile
profiles = df.groupby('repo').agg(
    entropy_mean=('entropy', 'mean'),
    entropy_std=('entropy', 'std'),
    entropy_cv=('entropy', lambda x: x.std() / x.mean()),  # coefficient of variation
    commit_mean=('commit_count', 'mean'),
    release_rate=('is_release', 'mean'),
    entropy_autocorr=('entropy', lambda x: x.autocorr(lag=1)),
).reset_index()

print("Repo profiles:")
print(profiles.to_string(index=False))

# cluster into 3 groups
scaler = StandardScaler()
X = scaler.fit_transform(profiles[['entropy_mean', 'entropy_std', 'entropy_cv', 'entropy_autocorr']])

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
profiles['cluster'] = kmeans.fit_predict(X)

print("\nClusters:")
for c in sorted(profiles['cluster'].unique()):
    repos = profiles[profiles['cluster'] == c]['repo'].tolist()
    print(f"  Cluster {c}: {repos}")

profiles.to_csv('outputs/repo_profiles.csv', index=False)
print("\nSaved outputs/repo_profiles.csv")