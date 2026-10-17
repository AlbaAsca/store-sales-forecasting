import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("v016", ROOT / "variants" / "V-016" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_cal():
    m = _load()
    c = m._cal(pd.DatetimeIndex(["2017-02-28", "2017-07-15", "2017-07-20", "2017-07-31", "2017-08-03"]))
    assert c["is_payday"].tolist() == [1, 1, 0, 1, 0]
    assert c["dias_desde_paga"].tolist() == [0, 0, 5, 0, 3]
    assert c["dias_a_fin_mes"].tolist() == [0, 16, 11, 0, 28]
