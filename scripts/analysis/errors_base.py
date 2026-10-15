"""Análisis de errores de una variante a partir de eval/results/<name>/preds-f*.csv.gz (nunca el holdout).

  python scripts/analysis/errors_base.py base-v0

Descompone el error cuadrático en log (lo que suma el RMSLE) por fold, familia, tienda, día de semana, horizonte,
día de paga, festivos y series con ceros; y muestra casos concretos. Incluye contrafactuales baratos calculados
solo con el histórico anterior al corte (perfil semanal, ceros recientes) para estimar qué arreglo da más.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
name = sys.argv[1] if len(sys.argv) > 1 else "base-v0"
pd.set_option("display.width", 200)

parts = []
for p in sorted((ROOT / "eval" / "results" / name).glob("preds-f*.csv.gz")):
    d = pd.read_csv(p, parse_dates=["date"])
    d["fold"] = p.name.split("-")[1].split(".")[0]
    d["h"] = (d["date"] - d["date"].min()).dt.days + 1
    parts.append(d)
df = pd.concat(parts, ignore_index=True)
df["e"] = np.log1p(df["pred"]) - np.log1p(df["sales"])
df["se"] = df["e"] ** 2
TOT = df["se"].sum()


def table(key, top=None, sort=True):
    g = df.groupby(key, observed=True).agg(n=("se", "size"), rmsle=("se", "mean"), sesgo=("e", "mean"),
                                            share=("se", "sum"))
    g["rmsle"] = np.sqrt(g["rmsle"])
    g["share"] = 100 * g["share"] / TOT
    if sort:
        g = g.sort_values("share", ascending=False)
    print(f"\n### por {key}\n" + (g.head(top) if top else g).round(3).to_string())
    return g


print(f"{name}: filas {len(df)}  RMSLE global {np.sqrt(df['se'].mean()):.4f}  sesgo log medio {df['e'].mean():+.4f}")
table("fold", sort=False)
table("family", top=12)
table("store_nbr", top=10)
df["dow"] = df["date"].dt.day_name().str[:3]
table("dow", sort=False)
table("h", sort=False)
df["paga"] = np.where(df["date"].dt.day.isin([15, 16]) | df["date"].dt.is_month_end | (df["date"].dt.day == 1),
                      "paga(15,16,fin,1)", "resto")
table("paga", sort=False)

# Festivos dentro de las ventanas
train = pd.read_csv(ROOT / "data" / "train.csv", parse_dates=["date"], dtype={"family": "category"})
hol = pd.read_csv(ROOT / "data" / "holidays_events.csv", parse_dates=["date"])
stores = pd.read_csv(ROOT / "data" / "stores.csv")
hol = hol[(hol["transferred"] == False) & (hol["type"] != "Work Day")]
nat = set(hol.loc[hol["locale"] == "National", "date"])
loc = hol[hol["locale"] != "National"].merge(stores, left_on="locale_name", right_on="city")[["date", "store_nbr"]]
loc2 = hol[hol["locale"] == "Regional"].merge(stores, left_on="locale_name", right_on="state")[["date", "store_nbr"]]
locset = set(map(tuple, pd.concat([loc, loc2]).values))
df["fest"] = np.where(df["date"].isin(nat), "nacional",
                      np.where([(d, s) in locset for d, s in zip(df["date"], df["store_nbr"])], "local/regional", "no"))
table("fest", sort=False)
print("festivos nacionales en folds:", sorted(d.date() for d in nat if pd.Timestamp("2017-05-28") <= d <= pd.Timestamp("2017-07-30")))

# Ceros
df["real0"] = df["sales"] == 0
df["pred0"] = df["pred"] == 0
table(["real0", "pred0"], sort=False)

# Series: errores por tienda×familia; ceros en el histórico reciente
cut = {f: g["date"].min() for f, g in df.groupby("fold")}
feats = []
for f, c in cut.items():
    h = train[(train["date"] < c) & (train["date"] >= c - pd.Timedelta(days=56))]
    last14 = h[h["date"] >= c - pd.Timedelta(days=14)]
    z = last14.groupby(["store_nbr", "family"], observed=True)["sales"].agg(z14=lambda s: (s == 0).mean())
    z["fold"] = f
    feats.append(z.reset_index())
feats = pd.concat(feats)
df = df.merge(feats, on=["fold", "store_nbr", "family"], how="left")
df["z14_bin"] = pd.cut(df["z14"], [-0.01, 0, 0.5, 0.99, 1], labels=["0 ceros", "<=50%", ">50%", "todo ceros"])
table("z14_bin", sort=False)

ser = df.groupby(["store_nbr", "family"], observed=True).agg(rmsle=("se", "mean"), sesgo=("e", "mean"),
                                                             share=("se", "sum"), venta=("sales", "mean"))
ser["rmsle"] = np.sqrt(ser["rmsle"]); ser["share"] = 100 * ser["share"] / TOT
ser = ser.sort_values("share", ascending=False)
print("\n### series que más error aportan\n", ser.head(15).round(3).to_string())
print(f"top 1% series ({len(ser)//100}) aportan {ser['share'].head(len(ser)//100).sum():.1f}% del error;"
      f" top 10%: {ser['share'].head(len(ser)//10).sum():.1f}%")

# Casos concretos: fold f1, diario
cases = [tuple(ser.index[0]), (44, "GROCERY I"), (1, "BEVERAGES")]
zero_series = ser[(ser["venta"] > 0)].sort_values("share", ascending=False)
for s, fam in cases:
    c = df[(df["store_nbr"] == s) & (df["family"] == fam) & (df["fold"] == "f1")]
    print(f"\n### caso tienda {s} × {fam} (f1)\n",
          c[["date", "dow", "sales", "pred", "e"]].round(2).to_string(index=False))

# Contrafactual 1: perfil de día de semana (solo histórico, 8 semanas) multiplicando la media 14d
cf = []
for f, c in cut.items():
    h = train[(train["date"] < c) & (train["date"] >= c - pd.Timedelta(days=56))].copy()
    h["dow"] = h["date"].dt.dayofweek
    m = h.groupby(["store_nbr", "family", "dow"], observed=True)["sales"].mean()
    mm = h.groupby(["store_nbr", "family"], observed=True)["sales"].mean()
    w = (m / mm.reindex(m.index.droplevel(2)).values).fillna(1).rename("w").reset_index()
    w["fold"] = f
    cf.append(w)
cf = pd.concat(cf)
df["dowi"] = df["date"].dt.dayofweek
df = df.merge(cf, left_on=["fold", "store_nbr", "family", "dowi"], right_on=["fold", "store_nbr", "family", "dow"],
              how="left", suffixes=("", "_y"))
df["w"] = df["w"].fillna(1)


def score(p):
    return df.assign(x=(np.log1p(p) - np.log1p(df["sales"])) ** 2).groupby("fold")["x"].mean().pipe(np.sqrt)


base = score(df["pred"])
print("\n### contrafactuales (RMSLE por fold)")
print("base             ", base.round(4).to_dict(), round(base.mean(), 4))
s1 = score(df["pred"] * df["w"])
print("x perfil semanal ", s1.round(4).to_dict(), round(s1.mean(), 4))
s2 = score(np.where(df["z14"] == 1, 0, df["pred"]))
print("ceros si 14d=0   ", s2.round(4).to_dict(), round(s2.mean(), 4))
# media geométrica (en log) en vez de aritmética: la métrica es en log
geo = []
for f, c in cut.items():
    h = train[(train["date"] < c) & (train["date"] >= c - pd.Timedelta(days=14))]
    g = np.expm1(np.log1p(h["sales"]).groupby([h["store_nbr"], h["family"]], observed=True).mean()).rename("g")
    geo.append(g.reset_index().assign(fold=f))
df = df.merge(pd.concat(geo), on=["fold", "store_nbr", "family"], how="left")
s3 = score(df["g"].fillna(0))
print("media en log 14d ", s3.round(4).to_dict(), round(s3.mean(), 4))
