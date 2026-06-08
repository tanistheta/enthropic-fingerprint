import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('data/combined_features.csv')

features = ['entropy', 'commit_count', 'avg_insertions', 'avg_deletions',
            'entropy_lag1', 'entropy_lag2', 'entropy_delta', 
            'commit_delta', 'churn_ratio', 'entropy_rolling3']
df = df.dropna(subset=features)

X = df[features].values
y = df['is_release'].values
repos = df['repo'].values

# cross-repo validation — train on 8, test on 1
results = []
for test_repo in df['repo'].unique():
    train_mask = repos != test_repo
    test_mask = repos == test_repo

    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    acc = (y_pred == y_test).mean()
    try:
        auc = roc_auc_score(y_test, y_prob)
    except:
        auc = float('nan')

    results.append({'repo': test_repo, 'accuracy': acc, 'auc': auc,
                    'n_test': len(y_test), 'n_release': y_test.sum()})
    print(f"{test_repo:12s} acc={acc:.3f}  auc={auc:.3f}  ({y_test.sum()}/{len(y_test)} release months)")

print()
results_df = pd.DataFrame(results)
print(f"Mean accuracy: {results_df['accuracy'].mean():.3f}")
print(f"Mean AUC:      {results_df['auc'].mean():.3f}")
results_df.to_csv('outputs/model_results.csv', index=False)
print("\nSaved outputs/model_results.csv")