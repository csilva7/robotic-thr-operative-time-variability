"""Paths and settings. On another machine, only the paths here need changing."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
OUT = ROOT / 'out'

# Data file names inside data/. To use your own local names without editing
# this file, create config_local.py (git-ignored) containing a FILES dict.
FILES = {'robotic': 'robotic.xlsx',   # HELLO study, n = 200
         'manual': 'manual.xlsx'}     # theatre records
try:
    from config_local import FILES  # noqa: F811
except ImportError:
    pass
ROBOTIC_FILE, MANUAL_FILE = DATA / FILES['robotic'], DATA / FILES['manual']
MANUAL_SHEET = 'Final Cohort'

SURGEON, PROCEDURE = 'MIDD', 'W941'
HELLO_START = pd.Timestamp('2019-08-01')
HELLO_END = pd.Timestamp('2023-05-25 23:59')
N_NEAREST = 200
THRESHOLDS = (70, 75, 90)
N_BOOT, SEED = 10_000, 2026
DPI = 300
COLOURS = {'robotic': '#3D7E98', 'near': '#C9822B', 'all': '#8C8C8C'}
