# Operative time variability: robot-arm assisted vs manual hybrid THR

Analysis code for *"Operative time variability in robot-arm assisted and manual
hybrid total hip replacement: a single-surgeon, two-hospital cohort study"*
(Journal of Robotic Surgery).

## Files

| File | What it does |
|---|---|
| `config.py` | File paths, HELLO recruitment dates, seed, colours. The only file to edit on another machine. |
| `data.py` | Loads the three spreadsheets, computes operative time and age, and selects the cohorts: robotic (n = 200), manual nearest 200 to the HELLO period (primary), all manual (n = 327, sensitivity) and manual inside the HELLO period (n = 31, descriptive). |
| `analysis.py` | All statistics. Writes `out/table1.csv` and `out/results.json`. |
| `figures.py` | Fig 1 (cumulative completion) and Fig 2 (distribution), 300 dpi PNG and TIFF. |
| `run_all.py` | Runs everything end to end. |

## Running

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run_all.py
```

Outputs go to `out/`. Bootstrap CIs use a fixed seed (2026), so reruns give identical numbers.

## Data (not included)

The data are not publicly available. They are patient-level hospital and study
records and are not included in this repository. To rerun the analysis with
authorised access, put the files in `data/` as:

- `robotic.xlsx`: robotic cohort (HELLO study), including `Age at surgery`
- `manual.xlsx`: theatre records, sheet `Final Cohort`, including `Age at surgery`

Age at surgery was calculated from routinely collected data during data
preparation, before analysis. The analysis files contain age only.

To keep other file names, create a git-ignored `config_local.py` containing
`FILES = {'robotic': '...', 'manual': '...'}`.

## Software

Python 3.9.6, with the package versions pinned in `requirements.txt`
(pandas 2.2.3, numpy 2.0.2, scipy 1.13.1, statsmodels 0.14.4, matplotlib 3.9.4,
openpyxl 3.1.5, pillow 11.3.0).

## Licence

MIT. See `LICENSE`.
