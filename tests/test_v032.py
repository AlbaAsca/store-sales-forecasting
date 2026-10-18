import importlib.util
from pathlib import Path

import numpy as np

from test_v025 import _data

ROOT = Path(__file__).resolve().parents[1]


def _load(monkeypatch):
    monkeypatch.setenv("HP_ROUNDS", "20")
    spec = importlib.util.spec_from_file_location("v032", ROOT / "variants" / "V-032" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_tweedie_blend_changes_prediction(monkeypatch):
    m = _load(monkeypatch)
    hist, fut = _data(500)
    monkeypatch.setenv("V032_W", "0")
    p0 = m.fit_predict(hist, fut, {"seed": 1})
    monkeypatch.setenv("V032_W", "0.2")
    p1 = m.fit_predict(hist, fut, {"seed": 1})
    assert len(p1) == len(fut) and np.isfinite(p1).all() and (p1 >= 0).all()
    assert not np.allclose(p0, p1)
    assert m.TW is False  # el flag se restablece tras mezclar
