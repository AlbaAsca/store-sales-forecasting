"""Residuo del mejor contrafactual (media log 14d + perfil log) según promoción del día vs. promo media reciente.
Solo folds (nunca holdout).  python scripts/analysis/errors_promo.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
train = pd.read_csv(ROOT / "data" / "train.csv", parse_dates=["date"], dtype={"family": "category"})
train["ls"] = np.log1p(train["sales"])
folds = json.loads((ROOT / "eval" / "folds.json").read_text(encoding="utf-8"))["folds"]
K = ["store_nbr", "family"]
out = []
for f in folds:
    c, e = pd.Timestamp(f["start"]), pd.Timestamp(f["end"])
    fut = train[(train["date"] >= c) & (train["date"] <= e)].copy()
    fut["dow"] = fut["date"].dt.dayofweek
    h = train[(train["date"] < c) & (train["date"] >= c - pd.Timedelta(days=56))].copy()
    h["dow"] = h["date"].dt.dayofweek
    h14 = h[h["date"] >= c - pd.Timedelta(days=14)]
    lm = h14.groupby(K, observed=True)["ls"].mean().rename("lm")
    pr = h14.groupby(K, observed=True)["onpromotion"].mean().rename("pr14")
    lmd = h.groupby(K + ["dow"], observed=True)["ls"].mean()
    lmm = h.groupby(K, observed=True)["ls"].mean()
    d = (lmd - lmm.reindex(lmd.index.droplevel(2)).values).rename("d")
    x = fut.join(lm, on=K).join(pr, on=K).join(d, on=K + ["dow"]).fillna({"lm": 0, "pr14": 0, "d": 0})
    x["e"] = (x["lm"] + x["d"]).clip(lower=0) - x["ls"]
    out.append(x)
x = pd.concat(out)
x["promo_vs_14d"] = pd.cut(x["onpromotion"] - x["pr14"], [-1e9, -2, -0.5, 0.5, 2, 10, 1e9],
                           labels=["<-2", "-2..-0.5", "≈igual", "+0.5..2", "+2..10", ">+10"])
tot = (x["e"] ** 2).sum()
g = x.groupby("promo_vs_14d", observed=True)["e"].agg(n="size", rmsle=lambda s: np.sqrt((s ** 2).mean()),
                                                       sesgo="mean", share=lambda s: 100 * (s ** 2).sum() / tot)
print(g.round(3).to_string())
