import numpy as np

from test_v005 import _data, _load


def test_v006_forma_con_poca_historia():
    hist, fut = _data(0)  # 120 dias: sin retardo 364 -> rasgos NaN
    p = np.asarray(_load("V-006").fit_predict(hist, fut, {}))
    assert len(p) == len(fut) and np.isfinite(p).all() and (p >= 0).all()


def test_v006_rasgos_anuales_sin_fuga():
    m = _load("V-006")
    n, T = 2, 500
    M = np.random.default_rng(0).random((n, T))
    P = np.zeros((n, T + 16))
    f1 = m._features(M, P, T, 0, n)
    M2 = M.copy()
    M2[:, T - 1] += 100  # cambiar el ultimo dia no debe afectar a ly_* (retardo 364)
    f2 = m._features(M2, P, T, 0, n)
    for k in ("ly_day", "ly_win", "ly_diff"):
        assert np.allclose(f1[k], f2[k], equal_nan=True)
    assert np.allclose(f1["ly_day"], M[:, T - 364:T - 364 + 16])
