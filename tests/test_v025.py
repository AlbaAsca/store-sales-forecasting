import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load(name, monkeypatch):
    monkeypatch.setenv("HP_ROUNDS", "20")
    spec = importlib.util.spec_from_file_location(name, ROOT / "variants" / name / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _data(n_days, closed=None):
    days = pd.date_range("2015-01-01", periods=n_days)
    rng = np.random.default_rng(0)
    rows = []
    for s in (1, 2, 3):
        for f in ("A", "B"):
            for i, d in enumerate(days):
                v = float(rng.integers(50, 100))
                if closed and s == 1 and closed[0] <= i < closed[1]:
                    v = 0.0
                rows.append((s, f, d, v, 0))
    hist = pd.DataFrame(rows, columns=["store_nbr", "family", "date", "sales", "onpromotion"])
    start = days[-1] + pd.Timedelta(days=1)
    fut = pd.DataFrame([(s, f, d, 0) for s in (1, 2, 3) for f in ("A", "B")
                        for d in pd.date_range(start, periods=16)],
                       columns=["store_nbr", "family", "date", "onpromotion"])
    return hist, fut


def test_runs_with_and_without_last_year(monkeypatch):
    m = _load("V-025", monkeypatch)
    for n in (500, 150):
        hist, fut = _data(n)
        p = m.fit_predict(hist, fut, {"seed": 1})
        assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()


def test_closed_store_last_year_not_copied(monkeypatch):
    # tienda 1 cerrada hace un año (ventana de los cortes anuales): V-025 no debe hundirla
    hist, fut = _data(500, closed=(90, 200))
    p18 = _load("V-018", monkeypatch).fit_predict(hist, fut, {"seed": 1})
    p25 = _load("V-025", monkeypatch).fit_predict(hist, fut, {"seed": 1})
    m = (fut["store_nbr"] == 1).to_numpy()
    assert np.log1p(p25[m]).mean() >= np.log1p(p18[m]).mean() - 1e-9
    assert p25[m].mean() > 30  # sigue prediciendo ventas normales (~75)
