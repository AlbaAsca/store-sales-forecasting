import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("v001", ROOT / "variants" / "V-001" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_factor_dia_semana():
    m = _load()
    dates = pd.date_range("2017-05-01", periods=70)  # termina en domingo
    sales = np.where(dates.dayofweek >= 5, 20.0, 10.0)
    hist = pd.DataFrame({"date": dates, "store_nbr": 1, "family": "A", "sales": sales})
    fut_dates = pd.date_range(dates[-1] + pd.Timedelta(days=1), periods=7)  # lun..dom
    fut = pd.DataFrame({"date": fut_dates, "store_nbr": 1, "family": "A"})
    pred = m.fit_predict(hist, fut, {})
    assert len(pred) == 7 and (pred >= 0).all()
    assert pred[5] > pred[0] * 1.5  # sábado > lunes
