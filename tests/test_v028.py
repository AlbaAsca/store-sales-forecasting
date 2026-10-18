import importlib.util
from pathlib import Path

import numpy as np

from test_v025 import _data

ROOT = Path(__file__).resolve().parents[1]


def _load(monkeypatch):
    monkeypatch.setenv("HP_ROUNDS", "20")
    spec = importlib.util.spec_from_file_location("v028", ROOT / "variants" / "V-028" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_agg_group_means(monkeypatch):
    m = _load(monkeypatch)
    store = np.array([0, 0, 1, 1])
    fam = np.array([0, 1, 0, 1])
    a = m._agg(np.array([1., 3., 5., 7.]), np.array([2., 2., 4., 4.]), store, fam)
    assert np.allclose(a["st_m7"], [2, 2, 6, 6])
    assert np.allclose(a["fam_m7"], [3, 5, 3, 5])
    assert np.allclose(a["st_trend"], a["st_m7"] - a["st_m28"])


def test_runs(monkeypatch):
    m = _load(monkeypatch)
    hist, fut = _data(500)
    p = m.fit_predict(hist, fut, {"seed": 1})
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()
