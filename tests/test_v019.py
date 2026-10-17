import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load(monkeypatch):
    monkeypatch.setenv("HP_ROUNDS", "20")
    spec = importlib.util.spec_from_file_location("v019", ROOT / "variants" / "V-019" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _data():
    days = pd.date_range("2016-01-01", periods=150)
    rng = np.random.default_rng(0)
    rows = []
    for s in (1, 2):
        for f in ("A", "B"):
            for i, d in enumerate(days):
                sales = float(rng.integers(5, 50))
                if (s, f) == (1, "A") and i >= 150 - 40:  # 40 dias a 0 antes del corte
                    sales = 0.0
                if (s, f) == (2, "B") and i == 149:  # vendio ayer: no es cero
                    sales = 0.0
                rows.append((s, f, d, sales, 0))
    hist = pd.DataFrame(rows, columns=["store_nbr", "family", "date", "sales", "onpromotion"])
    fut = pd.DataFrame([(s, f, d, 0) for s in (1, 2) for f in ("A", "B")
                        for d in pd.date_range("2016-05-30", periods=16)],
                       columns=["store_nbr", "family", "date", "onpromotion"])
    return hist, fut


def test_zero_rule(monkeypatch):
    m = _load(monkeypatch)
    hist, fut = _data()
    monkeypatch.setenv("ZERO_N", "28")
    p = m.fit_predict(hist, fut, {"seed": 1})
    assert len(p) == len(fut) and (p >= 0).all()
    zero_series = ((fut.store_nbr == 1) & (fut.family == "A")).to_numpy()
    assert (p[zero_series] == 0).all()
    assert (p[~zero_series] > 0).all()
    # con N mayor que la racha (40), la regla no actua
    monkeypatch.setenv("ZERO_N", "56")
    p2 = m.fit_predict(hist, fut, {"seed": 1})
    assert (p2[~zero_series] > 0).all()
    assert not (p2[zero_series] == 0).all()
