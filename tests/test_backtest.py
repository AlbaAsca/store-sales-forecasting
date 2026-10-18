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


TOY_MODEL = """
def fit_predict(history, future, ctx):
    mean = history.groupby(["store_nbr", "family"], observed=True)["sales"].mean().rename("pred")
    return future.join(mean, on=["store_nbr", "family"])["pred"].fillna(0).to_numpy()
"""


def test_backtest_corre_y_escribe_resumen(tmp_path, monkeypatch):
    # modelo de juguete fijo: el harness no debe depender de cuánta historia necesite la base vigente
    (tmp_path / "toy").mkdir()
    (tmp_path / "toy" / "model.py").write_text(TOY_MODEL)
    monkeypatch.setattr(backtest, "RESULTS", tmp_path)
    train, ctx = synthetic()
    s = backtest.run(tmp_path / "toy", "t", [{"id": "f1", "start": "2017-02-10", "end": "2017-02-25"}], train, ctx)
    assert (tmp_path / "t.json").exists() and 0 <= s["mean"] < 0.5 and set(s["folds"][0]["by_family"]) == {"A", "B"}


def summ(scores):
    return {"folds": [{"id": f"f{i}", "rmsle": v, "by_family": {"A": v}} for i, v in enumerate(scores)]}


def test_compare_veredicto():
    base = summ([0.50, 0.50, 0.50, 0.50])
    assert results.compare(base, summ([0.40, 0.45, 0.52, 0.48]))["accepted"]       # mejora media, empeora 1 fold
    assert not results.compare(base, summ([0.30, 0.55, 0.52, 0.48]))["accepted"]   # empeora 2 folds
    assert not results.compare(base, summ([0.50, 0.50, 0.50, 0.50]))["accepted"]   # empate: no aporta


def test_start_gap_detecta_hueco_25_dic():
    train, ctx = synthetic(days=60)
    train = train[train["date"] != pd.Timestamp("2017-02-09")]  # como el 25-dic: no hay fila ese día
    h, fut, _, _ = backtest.split(train, ctx, "2017-02-09", "2017-02-24")
    assert backtest.start_gap(h, fut) == 1  # future empieza el 10, history acaba el 8
    assert h["date"].max() + pd.Timedelta(days=1) != fut["date"].min()  # el start ingenuo falla
    h2, fut2, _, _ = backtest.split(train, ctx, "2017-02-12", "2017-02-27")
    assert backtest.start_gap(h2, fut2) == 0


def test_control_fold_aparte_de_la_media(tmp_path, monkeypatch):
    (tmp_path / "toy").mkdir()
    (tmp_path / "toy" / "model.py").write_text(TOY_MODEL)
    monkeypatch.setattr(backtest, "RESULTS", tmp_path)
    train, ctx = synthetic()
    f1 = [{"id": "f1", "start": "2017-02-10", "end": "2017-02-25"}]
    c1 = [{"id": "c1", "start": "2017-01-20", "end": "2017-02-04"}]
    s = backtest.run(tmp_path / "toy", "t", f1, train, ctx, control=c1)
    s0 = backtest.run(tmp_path / "toy", "t0", f1, train, ctx)
    assert s["mean"] == s0["mean"] and [r["id"] for r in s["control"]] == ["c1"] and "control" not in s0
    r = results.compare(s, s)
    assert [k for k, _, _ in r["control"]] == ["c1"] and [k for k, _, _ in r["folds"]] == ["f1"]


def test_open_mask_excluye_tiendas_cerradas():
    dates = pd.date_range("2016-08-01", periods=4)
    rows = [dict(date=d, store_nbr=s, family="A", sales=0.0 if (s == 1 or (s == 2 and i < 2)) else 5.0)
            for i, d in enumerate(dates) for s in (1, 2, 3)]
    m = backtest.open_mask(pd.DataFrame(rows))
    df = pd.DataFrame(rows)
    assert set(df["store_nbr"][~m]) == {1, 2}   # 100 % y 50 % de días a 0
    assert set(df["store_nbr"][m]) == {3}


def test_control_open_en_compare():
    a = {"folds": [{"id": "f1", "rmsle": 0.5, "by_family": {}}], "control": [{"id": "c1", "rmsle": 0.7, "rmsle_open": 0.4}]}
    b = {"folds": [{"id": "f1", "rmsle": 0.5, "by_family": {}}], "control": [{"id": "c1", "rmsle": 0.6, "rmsle_open": 0.3}]}
    assert results.compare(a, b)["control_open"] == [("c1", 0.4, 0.3)]
    assert results.compare(summ([0.5]), summ([0.5]))["control_open"] == []


def test_env_pasa_variables_al_modelo(monkeypatch):
    # el runner deniega «VAR=x python …»: --env es la forma permitida
    import os
    monkeypatch.setenv("ZERO_N", "56")  # registra el valor para que se restaure al acabar el test
    monkeypatch.setattr(backtest, "load_data", lambda: (None, None))
    monkeypatch.setattr(backtest, "run", lambda *a, **k: {"mean": 0.0, "std": 0.0, "secs": 0.0})
    backtest.main(["--src", "models/base", "--name", "t", "--quick", "--env", "ZERO_N=28"])
    assert os.environ["ZERO_N"] == "28"
