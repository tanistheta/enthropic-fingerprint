import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import spearmanr

plt.rcParams.update({
    'figure.facecolor': '#0d0d0d',
    'axes.facecolor': '#0d0d0d',
    'axes.edgecolor': '#333333',
    'axes.labelcolor': '#cccccc',
    'xtick.color': '#666666',
    'ytick.color': '#666666',
    'text.color': '#cccccc',
    'grid.color': '#1a1a1a',
    'grid.linewidth': 0.5,
    'font.family': 'monospace',
})

ACCENT = '#00ff88'
DIM = '#444444'
HIGHLIGHT = '#ff4466'

df = pd.read_csv('data/combined_features.csv')
profiles = pd.read_csv('outputs/repo_profiles.csv')

fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor('#0d0d0d')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

# --- Plot 1: entropy time series per repo ---
ax1 = fig.add_subplot(gs[0, :])
colors = plt.cm.plasma(np.linspace(0.15, 0.95, 9))
repos = df['repo'].unique()

for i, repo in enumerate(repos):
    sub = df[df['repo'] == repo].copy()
    sub = sub.sort_values('month')
    ax1.plot(range(len(sub)), sub['entropy'], alpha=0.7,
             linewidth=1.2, color=colors[i], label=repo)

ax1.set_title('ENTROPY OVER TIME - 9 REPOSITORIES (2018-2024)',
              fontsize=11, pad=12, color='#888888')
ax1.set_ylabel('shannon entropy (bits)', fontsize=9)
ax1.legend(loc='upper left', fontsize=8, framealpha=0.1, ncol=3, columnspacing=1)
ax1.grid(True, axis='y')
ax1.set_xlim(0, 83)

year_ticks = [0, 12, 24, 36, 48, 60, 72, 83]
year_labels = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '']
ax1.set_xticks(year_ticks)
ax1.set_xticklabels(year_labels)
ax1.set_xlabel('')

# --- Plot 2: commit volume vs entropy mean ---
ax2 = fig.add_subplot(gs[1, 0])
x = profiles['commit_mean']
y = profiles['entropy_mean']
r, p = spearmanr(x, y)

ax2.scatter(x, y, color=ACCENT, s=80, zorder=5, alpha=0.9)

offsets = {
    'rust': (6, 4), 'flask': (6, 4), 'vscode': (6, 4),
    'cpython': (6, 4), 'rails': (6, -12), 'numpy': (6, 4),
    'django': (-45, 4), 'sklearn': (6, -12), 'react': (6, -12),
}
for _, row in profiles.iterrows():
    ox, oy = offsets.get(row['repo'], (6, 4))
    ax2.annotate(row['repo'],
                 (row['commit_mean'], row['entropy_mean']),
                 textcoords='offset points', xytext=(ox, oy),
                 fontsize=8, color='#888888')

m, b = np.polyfit(np.log1p(x), y, 1)
xfit = np.linspace(x.min(), x.max(), 100)
ax2.plot(xfit, m * np.log1p(xfit) + b,
         color=ACCENT, alpha=0.3, linewidth=1.5, linestyle='--')

ax2.set_title(f'COMMIT VOLUME vs ENTROPY  (r={r:.2f}, p={p:.3f})',
              fontsize=10, pad=10, color='#888888')
ax2.set_xlabel('mean monthly commits', fontsize=9)
ax2.set_ylabel('mean entropy (bits)', fontsize=9)
ax2.grid(True)

# --- Plot 3: release vs non-release entropy distribution ---
ax3 = fig.add_subplot(gs[1, 1])
release = df[df['is_release'] == 1]['entropy'].dropna()
no_release = df[df['is_release'] == 0]['entropy'].dropna()

bins = np.linspace(0, 12, 40)
ax3.hist(no_release, bins=bins, alpha=0.5, color=DIM,
         label='non-release months', density=True)
ax3.hist(release, bins=bins, alpha=0.7, color=HIGHLIGHT,
         label='release months', density=True)

ax3.set_title('ENTROPY DISTRIBUTION: RELEASE vs NON-RELEASE',
              fontsize=10, pad=10, color='#888888')
ax3.set_xlabel('shannon entropy (bits)', fontsize=9)
ax3.set_ylabel('density', fontsize=9)
ax3.legend(fontsize=8, framealpha=0.1)
ax3.grid(True, axis='y')

fig.text(0.5, 0.01,
         'Entropic Fingerprint  //  commit volume drives entropy, not release behavior  //  9 repos · 754 months · 400k+ commits',
         ha='center', fontsize=8, color='#444444')

plt.savefig('outputs/entropic_fingerprint_v2.png',
            dpi=150, bbox_inches='tight',
            facecolor='#0d0d0d')
print("Saved outputs/entropic_fingerprint_v2.png")