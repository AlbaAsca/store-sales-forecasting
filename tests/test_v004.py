import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("v004", ROOT / "variants" / "V-004" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_lgbm_global_forma_orden_y_semana():
    m = _load()
    m.ROUNDS = 200
    dates = pd.date_range("2017-01-02", periods=140)  # empieza en lunes
    rows = []
    for fam, lvl in (("A", 10.0), ("Z", 0.0)):
        s = np.where(dates.dayofweek >= 5, lvl * 2, lvl)
        rows.append(pd.DataFrame({"date": dates, "store_nbr": 1, "family": fam, "sales": s}))
    hist = pd.concat(rows, ignore_index=True)
    fd = pd.date_range(dates[-1] + pd.Timedelta(days=1), periods=16)
    fut = pd.DataFrame({"date": list(fd) * 2, "store_nbr": 1, "family": ["A"] * 16 + ["Z"] * 16})
    pred = m.fit_predict(hist, fut, {"seed": 1})
    assert len(pred) == 32 and (pred >= 0).all() and np.isfinite(pred).all()
    assert np.allclose(pred[16:], 0, atol=0.5)
    a = pd.Series(pred[:16], index=fd)
    assert a[a.index.dayofweek >= 5].mean() > a[a.index.dayofweek < 3].mean() * 1.5
