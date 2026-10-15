import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load(v):
    spec = importlib.util.spec_from_file_location(v, ROOT / "variants" / v / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _data(promo_future):
    dates = pd.date_range("2017-03-01", periods=120)
    rows = []
    for s in (1, 2):
        for f in ("A", "B"):
            rows.append(pd.DataFrame({"date": dates, "store_nbr": s, "family": f,
                                      "sales": np.where(dates.dayofweek >= 5, 20.0, 10.0) + s,
                                      "onpromotion": (dates.day % 5 == 0).astype(int)}))
    hist = pd.concat(rows, ignore_index=True)
    fd = pd.date_range(dates[-1] + pd.Timedelta(days=1), periods=16)
    fut = pd.concat([pd.DataFrame({"date": fd, "store_nbr": s, "family": f, "onpromotion": promo_future})
                     for s in (1, 2) for f in ("A", "B")], ignore_index=True)
    return hist, fut


def test_v005_forma_y_no_negativo():
    hist, fut = _data(0)
    p = np.asarray(_load("V-005").fit_predict(hist, fut, {}))
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()
