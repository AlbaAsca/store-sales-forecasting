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
    dates = pd.date_range("2017-05-01", periods=70)
    hist = pd.DataFrame({"date": dates, "store_nbr": 1, "family": "A",
                         "sales": np.where(dates.dayofweek >= 5, 20.0, 10.0), "onpromotion": 0})
    fd = pd.date_range(dates[-1] + pd.Timedelta(days=1), periods=7)
    fut = pd.DataFrame({"date": fd, "store_nbr": 1, "family": "A", "onpromotion": promo_future})
    return hist, fut


def test_sin_promo_igual_a_v002():
    hist, fut = _data(0)
    p3 = _load("V-003").fit_predict(hist, fut, {})
    p2 = _load("V-002").fit_predict(hist.drop(columns="onpromotion"), fut.drop(columns="onpromotion"), {})
    assert len(p3) == 7 and (p3 >= 0).all()
    assert np.allclose(p3, p2)
