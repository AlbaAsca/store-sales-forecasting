"""Contrafactuales baratos sobre los folds (nunca holdout): qué daría cambiar la media aritmética por la media en log,
con y sin perfil semanal (en log). Solo usa ventas anteriores al corte de cada fold.

  python scripts/analysis/errors_cf.py
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

rows = {}
for f in folds:
    c, e = pd.Timestamp(f["start"]), pd.Timestamp(f["end"])
    fut = train[(train["date"] >= c) & (train["date"] <= e)].copy()
    fut["dow"] = fut["date"].dt.dayofweek
    h56 = train[(train["date"] < c) & (train["date"] >= c - pd.Timedelta(days=56))].copy()
    h56["dow"] = h56["date"].dt.dayofweek
    h14 = h56[h56["date"] >= c - pd.Timedelta(days=14)]
    am = h14.groupby(K, observed=True)["sales"].mean().rename("am")
    lm = h14.groupby(K, observed=True)["ls"].mean().rename("lm")
    # perfil multiplicativo (V-001) y perfil aditivo en log
    m = h56.groupby(K + ["dow"], observed=True)["sales"].mean()
    mm = h56.groupby(K, observed=True)["sales"].mean()
    w = (m / mm.reindex(m.index.droplevel(2)).values).replace([np.inf], np.nan).fillna(1).rename("w")
    lmd = h56.groupby(K + ["dow"], observed=True)["ls"].mean()
    lmm = h56.groupby(K, observed=True)["ls"].mean()
    d = (lmd - lmm.reindex(lmd.index.droplevel(2)).values).rename("d")
    # tendencia de los últimos 7 días frente a 14 (en log)
    l7 = h56[h56["date"] >= c - pd.Timedelta(days=7)].groupby(K, observed=True)["ls"].mean().rename("l7")
    x = fut.join(am, on=K).join(lm, on=K).join(l7, on=K).join(w, on=K + ["dow"]).join(d, on=K + ["dow"]).fillna(
        {"am": 0, "lm": 0, "l7": 0, "w": 1, "d": 0})
    y = x["ls"]
    cand = {
        "base (media 14d)": np.log1p(x["am"]),
        "V-001 (media x perfil)": np.log1p(x["am"] * x["w"]),
        "media log 14d": x["lm"],
        "media log 14d + perfil log": (x["lm"] + x["d"]).clip(lower=0),
        "media log 7d + perfil log": (x["l7"] + x["d"]).clip(lower=0),
        "log (7d+14d)/2 + perfil log": ((x["l7"] + x["lm"]) / 2 + x["d"]).clip(lower=0),
    }
    for k, p in cand.items():
        rows.setdefault(k, {})[f["id"]] = float(np.sqrt(((p - y) ** 2).mean()))
        rows[k][f["id"] + "_sesgo"] = float((p - y).mean())

t = pd.DataFrame(rows).T
t["media"] = t[[f["id"] for f in folds]].mean(axis=1)
print(t[[f["id"] for f in folds] + ["media"] + [f["id"] + "_sesgo" for f in folds]].round(4).to_string())
