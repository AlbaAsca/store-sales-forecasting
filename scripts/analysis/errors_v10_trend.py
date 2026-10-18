"""¿El sesgo de nivel de cada serie se explica con información disponible en el corte? (T-090)

  python scripts/analysis/errors_v10_trend.py V-031

Para cada serie×fold calcula, solo con días < corte: tendencia (log m14 − log m56), hueco con el año anterior
(log m14 − log del mismo tramo −364 d), fracción de ceros del año anterior; y mira cómo se relacionan con el sesgo.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
name = sys.argv[1] if len(sys.argv) > 1 else "V-031"
pd.set_option("display.width", 200)

parts = []
for p in sorted((ROOT / "eval" / "results" / name).glob("preds-f*.csv.gz")):
    d = pd.read_csv(p, parse_dates=["date"])
    d["fold"] = p.name.split("-")[1].split(".")[0]
    parts.append(d)
df = pd.concat(parts, ignore_index=True)
df["e"] = np.log1p(df["pred"]) - np.log1p(df["sales"])
df["se"] = df["e"] ** 2
TOT = df["se"].sum()

tr = pd.read_csv(ROOT / "data" / "train.csv", parse_dates=["date"], usecols=["date", "store_nbr", "family", "sales"])
M = tr.pivot_table(index=["store_nbr", "family"], columns="date", values="sales", observed=True)
L = np.log1p(M)
rows = []
for fo, g in df.groupby("fold"):
    a = g["date"].min()
    cols = L.columns
    w = lambda lo, hi: L.loc[:, (cols >= a + pd.Timedelta(days=lo)) & (cols < a + pd.Timedelta(days=hi))]
    f = pd.DataFrame({"m14": w(-14, 0).mean(1), "m56": w(-56, 0).mean(1), "ly": w(-364, -348).mean(1),
                      "ly0": (w(-364, -348) == 0).mean(1), "z14": (w(-14, 0) == 0).mean(1)})
    s = g.groupby(["store_nbr", "family"]).agg(bias=("e", "mean"), se=("se", "sum"), real=("sales", lambda x: np.log1p(x).mean()))
    rows.append(s.join(f).assign(fold=fo))
S = pd.concat(rows).reset_index()
S["trend"] = S["m14"] - S["m56"]
S["gap_ly"] = S["m14"] - S["ly"]
S = S[S["z14"] < 1]
print("correlación con el sesgo de la serie (ponderada igual):")
print(S[["bias", "trend", "gap_ly", "ly0", "z14"]].corr()["bias"].round(3).to_string())

for col, bins in [("trend", [-9, -.5, -.2, -.05, .05, .2, .5, 9]), ("gap_ly", [-9, -1, -.3, -.1, .1, .3, 1, 9])]:
    S["b"] = pd.cut(S[col], bins)
    t = S.groupby("b", observed=True).agg(n=("bias", "size"), sesgo=("bias", "mean"), share=("se", "sum"))
    t["share"] = (100 * t["share"] / TOT).round(1)
    print(f"\nsesgo medio por {col} (cada fila = serie×fold)\n" + t.round(3).to_string())

S["ly0b"] = pd.cut(S["ly0"], [-.01, 0, .5, .99, 1], labels=["0", "<=50%", "50-99%", "100%"])
t = S.groupby("ly0b", observed=True).agg(n=("bias", "size"), sesgo=("bias", "mean"), share=("se", "sum"))
t["share"] = (100 * t["share"] / TOT).round(1)
print("\nsesgo por ceros en el mismo tramo del año anterior (series vivas ahora)\n" + t.round(3).to_string())

# GROCERY II: nivel nacional reciente vs año anterior
g2 = M.xs("GROCERY II", level="family").sum()
print("\nGROCERY II total nacional, media por mes (2016-01..2017-07):")
print(g2[g2.index >= "2016-01-01"].resample("MS").mean().round(0).to_string())
