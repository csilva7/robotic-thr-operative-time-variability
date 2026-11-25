"""All statistics. Writes out/table1.csv and out/results.json."""
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
import config as C
import data


def describe(df):
    y = df.time.to_numpy()
    q1, med, q3, p90 = np.percentile(y, [25, 50, 75, 90])
    d = dict(n=len(y), female_n=int(df.female.sum()), female_pct=100 * df.female.mean(),
             age_mean=df.age.mean(), age_sd=df.age.std(ddof=1),
             mean=y.mean(), sd=y.std(ddof=1), median=med, q1=q1, q3=q3, min=y.min(), max=y.max(),
             cv=100 * y.std(ddof=1) / y.mean(), p90=p90)
    for t in C.THRESHOLDS:
        d[f'gt{t}_n'] = int((y > t).sum())
        d[f'gt{t}_pct'] = 100 * d[f'gt{t}_n'] / len(y)
    return d


def welch(a, b):
    """Mean of a minus mean of b, with Welch 95% CI and p."""
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    diff, half = a.mean() - b.mean(), stats.t.ppf(0.975, df) * np.sqrt(va + vb)
    return dict(diff=diff, lo=diff - half, hi=diff + half, p=stats.ttest_ind(a, b, equal_var=False).pvalue)


def sd_ratio(man, rob):
    """Manual/robotic SD ratio; percentile bootstrap, each cohort resampled independently."""
    rng = np.random.default_rng(C.SEED)
    bm = rng.choice(man, (C.N_BOOT, len(man))).std(axis=1, ddof=1)
    br = rng.choice(rob, (C.N_BOOT, len(rob))).std(axis=1, ddof=1)
    lo, hi = np.percentile(bm / br, [2.5, 97.5])
    return dict(ratio=man.std(ddof=1) / rob.std(ddof=1), lo=lo, hi=hi)


def threshold(man, rob, t):
    """Fisher's exact test; risk ratio manual/robotic with log-method 95% CI."""
    a, b, n1, n2 = int((man > t).sum()), int((rob > t).sum()), len(man), len(rob)
    rr = (a / n1) / (b / n2)
    se = np.sqrt(1 / a - 1 / n1 + 1 / b - 1 / n2)
    return dict(manual_n=a, robotic_n=b, rr=rr, lo=rr * np.exp(-1.96 * se), hi=rr * np.exp(1.96 * se),
                p=stats.fisher_exact([[a, n1 - a], [b, n2 - b]])[1])


def age_adjusted(man, rob):
    """OLS time ~ group + age (HC3); then Levene on the residuals by group."""
    d = pd.concat([rob.assign(manual=0), man.assign(manual=1)], ignore_index=True)[['time', 'age', 'manual']]
    f = smf.ols('time ~ manual + age', d).fit(cov_type='HC3')
    lo, hi = f.conf_int().loc['manual']
    r_man, r_rob = f.resid[d.manual == 1], f.resid[d.manual == 0]
    return dict(diff=f.params['manual'], lo=lo, hi=hi, p=f.pvalues['manual'],
                resid_sd_robotic=r_rob.std(ddof=1), resid_sd_manual=r_man.std(ddof=1),
                resid_levene_p=stats.levene(r_rob, r_man, center='mean').pvalue)


def compare(man, rob):
    y, x = man.time.to_numpy(), rob.time.to_numpy()
    return dict(mean_diff_manual_minus_robotic=welch(y, x),
                mann_whitney_p=stats.mannwhitneyu(x, y, alternative='two-sided').pvalue,
                levene_p=stats.levene(x, y, center='mean').pvalue,
                sd_ratio=sd_ratio(y, x),
                thresholds={f'gt{t}': threshold(y, x, t) for t in C.THRESHOLDS},
                age_adjusted=age_adjusted(man, rob),
                age_diff_robotic_minus_manual=welch(rob.age.to_numpy(), man.age.to_numpy()))


def robotic_trend(rob):
    """OLS time ~ years since the first robotic operation (HC3)."""
    d = rob.assign(years=(rob.date - rob.date.min()).dt.days / 365.25)
    f = smf.ols('time ~ years', d).fit(cov_type='HC3')
    lo, hi = f.conf_int().loc['years']
    return dict(slope_per_year=f.params['years'], lo=lo, hi=hi)


TABLE1 = [('n', '{n}'),
          ('Female, n (%)', '{female_n} ({female_pct:.1f})'),
          ('Age, years, mean (SD)', '{age_mean:.1f} ({age_sd:.1f})'),
          ('Operative time, min, mean (SD)', '{mean:.1f} ({sd:.1f})'),
          ('Median (IQR)', '{median:.0f} ({q1:.0f}–{q3:.0f})'),
          ('Range', '{min:.0f}–{max:.0f}'),
          ('Coefficient of variation, %', '{cv:.1f}'),
          ('90th centile', '{p90:.0f}')] + \
         [(f'Over {t} min, n (%)', f'{{gt{t}_n}} ({{gt{t}_pct:.1f}})') for t in C.THRESHOLDS]
COLUMNS = [('robotic', 'Robot-arm assisted'), ('near', 'Manual (nearest 200)'), ('all', 'Manual (all cases)')]


def main(g=None):
    g = g or data.cohorts()
    C.OUT.mkdir(exist_ok=True)
    desc = {k: describe(g[k]) for k, _ in COLUMNS}
    pd.DataFrame({lab: [f.format(**desc[k]) for _, f in TABLE1] for k, lab in COLUMNS},
                 index=[r for r, _ in TABLE1]).to_csv(C.OUT / 'table1.csv', encoding='utf-8-sig')
    inp = describe(g['inperiod'])
    results = dict(descriptives=desc,
                   robotic_vs_manual_nearest200=compare(g['near'], g['robotic']),
                   robotic_vs_manual_all=compare(g['all'], g['robotic']),
                   robotic_trend=robotic_trend(g['robotic']),
                   manual_in_hello_period={k: inp[k] for k in ('n', 'mean', 'sd', 'median', 'q1', 'q3', 'p90', 'gt90_n')})
    with open(C.OUT / 'results.json', 'w') as fh:
        json.dump(results, fh, indent=2, default=lambda o: o.item())
    return results


if __name__ == '__main__':
    main()
