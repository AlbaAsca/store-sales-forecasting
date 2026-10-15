import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("v002", ROOT / "variants" / "V-002" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_log_perfil_semanal_y_ceros():
    m = _load()
    dates = pd.date_range("2017-05-01", periods=70)  # termina en domingo
    sales = np.where(dates.dayofweek >= 5, 20.0, 10.0)
    hist = pd.DataFrame({
        "date": list(dates) * 2,
        "store_nbr": 1,
        "family": ["A"] * 70 + ["Z"] * 70,
        "sales": np.concatenate([sales, np.zeros(70)]),
    })
    fut_dates = pd.date_range(dates[-1] + pd.Timedelta(days=1), periods=7)
    fut = pd.DataFrame({"date": list(fut_dates) * 2, "store_nbr": 1, "family": ["A"] * 7 + ["Z"] * 7})
    pred = m.fit_predict(hist, fut, {})
    assert len(pred) == 14 and (pred >= 0).all()
    assert pred[5] > pred[0] * 1.5  # sábado > lunes
    assert np.allclose(pred[7:], 0)  # serie de ceros -> 0
