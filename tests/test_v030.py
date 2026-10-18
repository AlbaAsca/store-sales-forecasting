import importlib.util
from pathlib import Path

import numpy as np

from test_v025 import _data

ROOT = Path(__file__).resolve().parents[1]


def _load(monkeypatch):
    monkeypatch.setenv("HP_ROUNDS", "20")
    spec = importlib.util.spec_from_file_location("v030", ROOT / "variants" / "V-030" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_configs_have_distinct_windows(monkeypatch):
    m = _load(monkeypatch)
    assert len(m.CONFIGS) == 3
    assert len({c[1] for c in m.CONFIGS}) == 3


def test_runs_and_averages(monkeypatch):
    m = _load(monkeypatch)
    hist, fut = _data(500)
    p = m.fit_predict(hist, fut, {"seed": 1})
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()
    monkeypatch.setenv("V030_CFGS", "0")
    p0 = m.fit_predict(hist, fut, {"seed": 1})
    assert not np.allclose(p, p0)
