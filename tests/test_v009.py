import numpy as np
import pytest

from test_v005 import _data, _load


@pytest.mark.parametrize("mode", ["rec", "avg"])
def test_v009_forma_y_no_negativo(monkeypatch, mode):
    monkeypatch.setenv("V009_MODE", mode)
    hist, fut = _data(0)
    m = _load("V-009")
    p = np.asarray(m.fit_predict(hist, fut, {}))
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()
