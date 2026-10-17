import numpy as np

from test_v005 import _data, _load


def test_v008_modelos_por_horizonte_forma_y_no_negativo():
    hist, fut = _data(0)
    m = _load("V-008")
    p = np.asarray(m.fit_predict(hist, fut, {}))
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()
