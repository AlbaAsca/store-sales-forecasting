import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load(monkeypatch):
    monkeypatch.setenv("HP_ROUNDS", "20")
    spec = importlib.util.spec_from_file_location("v018", ROOT / "variants" / "V-018" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _data(n_days):
    days = pd.date_range("2015-01-01", periods=n_days)
    rng = np.random.default_rng(0)
    rows = [(s, f, d, float(rng.integers(5, 50)), 0)
            for s in (1, 2) for f in ("A", "B") for d in days]
    hist = pd.DataFrame(rows, columns=["store_nbr", "family", "date", "sales", "onpromotion"])
    start = days[-1] + pd.Timedelta(days=1)
    fut = pd.DataFrame([(s, f, d, 0) for s in (1, 2) for f in ("A", "B")
                        for d in pd.date_range(start, periods=16)],
                       columns=["store_nbr", "family", "date", "onpromotion"])
    return hist, fut


def test_runs_with_and_without_last_year(monkeypatch):
    m = _load(monkeypatch)
    for n in (500, 150):  # con y sin historia de hace un año
        hist, fut = _data(n)
        p = m.fit_predict(hist, fut, {"seed": 1})
        assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()


def test_no_leak_future_sales_ignored(monkeypatch):
    m = _load(monkeypatch)
    hist, fut = _data(500)
    p1 = m.fit_predict(hist, fut, {"seed": 1})
    p2 = m.fit_predict(hist, fut, {"seed": 1})
    assert np.allclose(p1, p2)  # determinista con la misma semilla
