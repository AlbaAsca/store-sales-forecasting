import numpy as np

from test_v005 import _data, _load


def test_v015_forma_y_no_negativo():
    hist, fut = _data(0)
    m = _load("V-015")
    p = np.asarray(m.fit_predict(hist, fut, {}))
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()


def test_v015_zero_feats():
    m = _load("V-015")
    past = np.ones((2, 60))
    past[0, -3:] = 0.0  # 3 ceros al final
    past[1, :] = 0.0    # todo ceros
    f = m._zero_feats(past)
    assert f["since_nz"][0] == 3 and f["since_nz"][1] == 56
    assert np.isclose(f["zfrac14"][0], 3 / 14) and f["zfrac56"][1] == 1.0
