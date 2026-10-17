import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("v017", ROOT / "variants" / "V-017" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_holiday_mats():
    m = _load()
    hol = pd.DataFrame({
        "date": pd.to_datetime(["2017-08-10", "2017-08-11", "2017-08-12", "2017-08-13", "2017-08-14"]),
        "type": ["Holiday", "Transfer", "Holiday", "Holiday", "Work Day"],
        "locale": ["National", "National", "Local", "Regional", "National"],
        "locale_name": ["Ecuador", "Ecuador", "Quito", "Guayas", "Ecuador"],
        "transferred": [True, False, False, False, False]})
    st = pd.DataFrame({"store_nbr": [1, 2], "city": ["Quito", "Guayaquil"], "state": ["Pichincha", "Guayas"]})
    series = pd.DataFrame({"store_nbr": [1, 2]})
    H = m._holiday_mats({"holidays": hol, "stores": st}, series, pd.date_range("2017-08-10", periods=5))
    assert H["hol_nat"].tolist() == [[0, 1, 0, 0, 0]] * 2
    assert H["hol_loc"].tolist() == [[0, 0, 1, 0, 0], [0] * 5]
    assert H["hol_reg"].tolist() == [[0] * 5, [0, 0, 0, 1, 0]]
    assert H["event_nat"].sum() == 0
