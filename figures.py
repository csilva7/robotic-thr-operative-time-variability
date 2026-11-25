"""Fig 1 (cumulative completion) and Fig 2 (distribution): 300 dpi PNG + TIFF in out/."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import config as C
import data

plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
XLAB = 'Operative time, incision to closure (min)'
GROUPS = [('robotic', 'Robot-arm assisted'), ('near', 'Manual (nearest 200)'), ('all', 'Manual (all cases)')]


def save(fig, name):
    png = C.OUT / f'{name}.png'
    fig.savefig(png, dpi=C.DPI, bbox_inches='tight', facecolor='white')
    Image.open(png).convert('RGB').save(C.OUT / f'{name}.tiff', dpi=(C.DPI, C.DPI), compression='tiff_lzw')
    plt.close(fig)


def fig1(g):
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    for k, lab in GROUPS:
        x = np.sort(g[k].time.to_numpy())
        ax.step(x, np.arange(1, len(x) + 1) / len(x) * 100, where='post', color=C.COLOURS[k],
                lw=1.4 if k == 'all' else 2, ls='--' if k == 'all' else '-', label=lab)
    ax.axhline(90, ls=':', lw=0.9, color='#888888')
    ax.text(139, 91, '90% of operations completed', ha='right', va='bottom', fontsize=7.5, color='#666666')
    for k, dx, dy, ha in (('robotic', -2, 3, 'right'), ('near', 2, -7, 'left')):
        p = np.percentile(g[k].time, 90)
        ax.plot([p, p], [0, 90], ls=':', lw=0.9, color=C.COLOURS[k])
        ax.scatter([p], [90], s=30, color=C.COLOURS[k], edgecolor='white', linewidth=0.8, zorder=5)
        ax.text(p + dx, 90 + dy, f'{p:.0f} min', ha=ha, fontsize=8.5, color=C.COLOURS[k])
    ax.set(xlim=(40, 140), ylim=(0, 102), xlabel=XLAB, ylabel='Operations completed (%)')
    ax.legend(loc='lower right', frameon=False, fontsize=8)
    save(fig, 'Fig1_cumulative_completion')


def fig2(g):
    fig, ax = plt.subplots(figsize=(6, 4.6))
    rng = np.random.default_rng(C.SEED)  # jitter only
    ys = [g[k].time.to_numpy() for k, _ in GROUPS]
    bp = ax.boxplot(ys, positions=range(3), widths=0.55, whis=1.5, patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', lw=1.6))
    for box, (k, _) in zip(bp['boxes'], GROUPS):
        box.set(facecolor=C.COLOURS[k], alpha=0.85)
    top = max(y.max() for y in ys)
    for i, y in enumerate(ys):
        ax.scatter(i + rng.uniform(-0.17, 0.17, len(y)), y, s=7, facecolors='none', edgecolors='#555555',
                   linewidths=0.4, alpha=0.6, zorder=3)
        ax.scatter([i], [y.mean()], marker='D', s=26, color='white', edgecolors='black', zorder=4)
        ax.text(i, top + 32, f'n = {len(y)}\nmean {y.mean():.1f}\nSD {y.std(ddof=1):.1f}',
                ha='center', va='top', fontsize=8)
    ax.set_xticks(range(3))
    ax.set_xticklabels([lab.replace(' (', '\n(') for _, lab in GROUPS])
    ax.set(ylabel=XLAB, ylim=(30, top + 36))
    save(fig, 'Fig2_operative_time_distribution')


def main(g=None):
    g = g or data.cohorts()
    C.OUT.mkdir(exist_ok=True)
    fig1(g)
    fig2(g)


if __name__ == '__main__':
    main()
