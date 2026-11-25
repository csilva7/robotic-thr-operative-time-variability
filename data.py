"""Load, clean and select the cohorts. Nothing patient-level is written to disk."""
import datetime as dt
import numpy as np
import pandas as pd
import config as C


def _minutes(v):
    """OP_DurationSurg is hh:mm (text or a time object) -> minutes."""
    if isinstance(v, dt.time):
        return v.hour * 60 + v.minute
    h, m = str(v).split(':')[:2]
    return int(h) * 60 + int(m)


def load_robotic():
    h = pd.read_excel(C.ROBOTIC_FILE, sheet_name=0)
    return pd.DataFrame({'time': h['OP_DurationSurg'].map(_minutes).astype(float),
                         'age': h['Age at surgery'].astype(float),
                         'female': h['Gender'].astype(str).str.strip().str.lower().str.startswith('f'),
                         'date': pd.to_datetime(h['OP_DateSurgery'])})


def load_manual():
    d = pd.read_excel(C.MANUAL_FILE, sheet_name=C.MANUAL_SHEET)
    m = d[(d.Surgeon_1 == C.SURGEON) & (d.Procedure_Code == C.PROCEDURE)].reset_index(drop=True)
    out = pd.DataFrame({'time': m['Operative_Time_Minutes'].astype(float),
                        'age': m['Age at surgery'].astype(float),
                        'female': m['Sex'].astype(str).str.upper().eq('FEMALE'),
                        'dt': m['Knife_to_Skin_Date_Time']})
    lo, hi = C.HELLO_START, C.HELLO_END  # distance in days from the HELLO recruitment period
    out['dist'] = np.where(out.dt < lo, (lo - out.dt).dt.days, np.where(out.dt > hi, (out.dt - hi).dt.days, 0))
    return out


def cohorts():
    rob, m = load_robotic(), load_manual()
    return {'robotic': rob,
            'near': m.nsmallest(C.N_NEAREST, 'dist', keep='first'),  # primary comparison
            'all': m,                                                # sensitivity analysis
            'inperiod': m[m.dist == 0]}                              # descriptive only
