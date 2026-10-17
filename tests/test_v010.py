import numpy as np

from test_v005 import _data, _load


def test_v010_forma_no_negativo_y_semilla(monkeypatch):
    hist, fut = _data(0)
    m = _load("V-010")
    monkeypatch.setattr(m, "SEEDS", (0, 1))
    monkeypatch.setattr(m, "WINDOW_STARTS", (None, "2017-02-01"))
    p = np.asarray(m.fit_predict(hist, fut, {}))
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()
    p2 = np.asarray(m.fit_predict(hist, fut, {"seed": 1}))
    assert np.isfinite(p2).all() and not np.allclose(p, p2)
