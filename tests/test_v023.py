import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = 500


def _load(monkeypatch):
    monkeypatch.setenv("HP_ROUNDS", "20")
    spec = importlib.util.spec_from_file_location("v023", ROOT / "variants" / "V-023" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _data():
    days = pd.date_range("2015-01-01", periods=T)
    rng = np.random.default_rng(0)
    rows = []
    for f in ("A", "B", "C"):
        for i, d in enumerate(days):
            sales = float(rng.integers(5, 50))
            if f in ("A", "B") and i >= T - 60:  # 60 dias a 0 antes del corte
                sales = 0.0
            if f == "A" and not (T - 364 - 7 <= i < T - 364 + 23):
                pass
            if f == "B" and T - 364 - 7 <= i < T - 364 + 23:
                sales = 0.0  # B: tampoco vendia el año anterior -> muerta
            rows.append((1, f, d, sales, 0))
    # A: vendio el año anterior en la ventana (aleatorio >0 ya) -> temporada, no se toca
    hist = pd.DataFrame(rows, columns=["store_nbr", "family", "date", "sales", "onpromotion"])
    start = days[-1] + pd.Timedelta(days=1)
    fut = pd.DataFrame([(1, f, d, 0) for f in ("A", "B", "C") for d in pd.date_range(start, periods=16)],
                       columns=["store_nbr", "family", "date", "onpromotion"])
    return hist, fut


def test_zero_rule_seasonal_exception(monkeypatch):
    m = _load(monkeypatch)
    hist, fut = _data()
    p = m.fit_predict(hist, fut, {"seed": 1})
    assert len(p) == len(fut) and (p >= 0).all()
    fam = fut.family.to_numpy()
    assert (p[fam == "B"] == 0).all()   # muerta de verdad
    assert (p[fam == "A"] > 0).all()    # vendio en las mismas fechas del año anterior
    assert (p[fam == "C"] > 0).all()
