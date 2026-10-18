"""Contrafactual: ¿corregir el sesgo por familia (o tienda, o serie) con el sesgo del fold anterior ayuda? (T-090)

  python scripts/analysis/errors_v10_shift.py V-031

Los folds son contiguos (f4 el más antiguo, f1 el más reciente): el error del fold anterior es conocido en el corte
del siguiente, así que esto imita «medir el error del modelo en los 16 días previos al corte y restarlo». Sin fuga.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
name = sys.argv[1] if len(sys.argv) > 1 else "V-031"
parts = []
for p in sorted((ROOT / "eval" / "results" / name).glob("preds-f*.csv.gz")):
    d = pd.read_csv(p, parse_dates=["date"])
    d["fold"] = p.name.split("-")[1].split(".")[0]
    parts.append(d)
df = pd.concat(parts, ignore_index=True)
df["e"] = np.log1p(df["pred"]) - np.log1p(df["sales"])
prev = {"f1": "f2", "f2": "f3", "f3": "f4"}
print(df.groupby("fold")["date"].agg(["min", "max"]).to_string())
ev = df[df["fold"].isin(prev)]
base = ev.groupby("fold")["e"].apply(lambda e: np.sqrt((e ** 2).mean()))
print("\nbase (f1-f3):", base.round(4).to_dict(), round(float(np.sqrt((ev['e'] ** 2).mean())), 4))
for keys in (["family"], ["store_nbr"], ["store_nbr", "family"]):
    b = df.groupby(["fold"] + keys)["e"].mean().rename("b").reset_index()
    b["fold"] = b["fold"].map({v: k for k, v in prev.items()})
    x = ev.merge(b.dropna(subset=["fold"]), on=["fold"] + keys, how="left")
    for k in (0.25, 0.5, 1.0):
        e2 = x["e"] - k * x["b"].fillna(0)
        res = x.assign(e2=e2).groupby("fold")["e2"].apply(lambda e: np.sqrt((e ** 2).mean()))
        print(f"corrige {'+'.join(keys):18s} x{k}: {res.round(4).to_dict()}  media {np.sqrt((e2 ** 2).mean()):.4f}")

tr = pd.read_csv(ROOT / "data" / "train.csv", parse_dates=["date"])
s = tr[(tr["store_nbr"] == 45) & (tr["family"] == "SCHOOL AND OFFICE SUPPLIES")].set_index("date")["sales"]
print("\ntienda 45 material escolar, suma semanal jul-sep 2016 y jul-ago 2017:")
for y in ("2016", "2017"):
    print(y, s[f"{y}-07-01":f"{y}-09-30"].resample("W-SUN").sum().astype(int).tolist())
