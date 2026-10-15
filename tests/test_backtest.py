"""El backtest no deja ver el futuro, la métrica es la de Kaggle y el comparador decide bien."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import backtest  # noqa: E402
import results  # noqa: E402


def synthetic(days=60):
    dates = pd.date_range("2017-01-01", periods=days)
    rows = [dict(id=i, date=d, store_nbr=s, family=f, sales=float(s * 10 + d.dayofweek), onpromotion=0)
            for i, (d, s, f) in enumerate((d, s, f) for d in dates for s in (1, 2) for f in ("A", "B"))]
    train = pd.DataFrame(rows).astype({"family": "category"})
    tx = pd.DataFrame({"date": dates, "store_nbr": 1, "transactions": 100})
    ctx = {"oil": pd.DataFrame({"date": dates, "dcoilwtico": 50.0}), "holidays": pd.DataFrame(columns=["date"]),
           "stores": pd.DataFrame({"store_nbr": [1, 2]}), "transactions": tx}
    return train, ctx


def test_rmsle_igual_que_kaggle():
    assert backtest.rmsle([0, 1, 10], [0, 1, 10]) == 0
    assert backtest.rmsle([0], [np.e - 1]) == pytest.approx(1.0)
    assert backtest.rmsle([5], [-3]) == backtest.rmsle([5], [0])  # negativas se recortan a 0


def test_split_sin_fugas():
    train, ctx = synthetic()
    h, fut, y, c = backtest.split(train, ctx, "2017-02-10", "2017-02-25")
    assert h["date"].max() < pd.Timestamp("2017-02-10")
    assert "sales" not in fut.columns and len(fut) == len(y) == 16 * 4
    assert c["transactions"]["date"].max() < pd.Timestamp("2017-02-10")


def test_base_corre_y_escribe_resumen(tmp_path, monkeypatch):
    monkeypatch.setattr(backtest, "RESULTS", tmp_path)
    train, ctx = synthetic()
    s = backtest.run(ROOT / "models" / "base", "t", [{"id": "f1", "start": "2017-02-10", "end": "2017-02-25"}], train, ctx)
    assert (tmp_path / "t.json").exists() and 0 <= s["mean"] < 0.5 and set(s["folds"][0]["by_family"]) == {"A", "B"}


def summ(scores):
    return {"folds": [{"id": f"f{i}", "rmsle": v, "by_family": {"A": v}} for i, v in enumerate(scores)]}


def test_compare_veredicto():
    base = summ([0.50, 0.50, 0.50, 0.50])
    assert results.compare(base, summ([0.40, 0.45, 0.52, 0.48]))["accepted"]       # mejora media, empeora 1 fold
    assert not results.compare(base, summ([0.30, 0.55, 0.52, 0.48]))["accepted"]   # empeora 2 folds
    assert not results.compare(base, summ([0.50, 0.50, 0.50, 0.50]))["accepted"]   # empate: no aporta
