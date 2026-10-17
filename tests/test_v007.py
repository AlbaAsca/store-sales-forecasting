import numpy as np

from test_v005 import _data, _load


def test_v007_tweedie_forma_y_no_negativo():
    hist, fut = _data(0)
    m = _load("V-007")
    assert m.PARAMS["objective"] == "tweedie"
    p = np.asarray(m.fit_predict(hist, fut, {}))
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()
