"""Análisis de errores de base-v9 para el brainstorming v10 (T-090). Solo folds de prácticas, nunca el holdout.

  python scripts/analysis/errors_v10.py V-031

Responde: ¿el error es de nivel (la serie entera desplazada) o de ruido diario? ¿hay desplazamientos comunes por tienda
o por familia (que un ajuste agregado podría corregir)? ¿cómo va con promo? ¿qué pasa en las series peores (contexto
del año anterior y de los 28 días previos)? ¿cuánto se ganaría con un techo de "nivel perfecto"?
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
name = sys.argv[1] if len(sys.argv) > 1 else "V-031"
pd.set_option("display.width", 200)


def load(pattern):
    parts = []
    for p in sorted((ROOT / "eval" / "results" / name).glob(pattern)):
        d = pd.read_csv(p, parse_dates=["date"])
        d["fold"] = p.name.split("-")[1].split(".")[0]
        d["h"] = (d["date"] - d["date"].min()).dt.days + 1
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    d["e"] = np.log1p(d["pred"]) - np.log1p(d["sales"])
    d["se"] = d["e"] ** 2
    return d


df = load("preds-f*.csv.gz")
TOT = df["se"].sum()
r = lambda s: np.sqrt(s.mean())
print(f"{name}: RMSLE {r(df['se']):.4f}")

# 1) Nivel vs ruido: error = sesgo medio de la serie en la ventana + desviación diaria
print("\n## 1. Descomposición nivel / día (por serie×fold)")
for keys, lab in [(["fold", "store_nbr", "family"], "serie"), (["fold", "store_nbr"], "tienda entera"),
                  (["fold", "family"], "familia en todo el país"), (["fold"], "fold entero")]:
    m = df.groupby(keys, observed=True)["e"].transform("mean")
    share = 100 * (m ** 2).sum() / TOT
    print(f"  quitar el sesgo medio por {lab:25s}: RMSLE {r((df['e'] - m) ** 2):.4f}  (el nivel explica {share:.1f}%)")

# 1b) Nivel de serie: cuánto del sesgo ya era visible en el sesgo del fold anterior (persistencia del error)
sb = df.groupby(["fold", "store_nbr", "family"], observed=True)["e"].mean().unstack("fold")
print("\n  correlación del sesgo de cada serie entre folds (si alta, el error de nivel es sistemático):")
print(sb.corr().round(2).to_string())

# 1c) Sesgo de serie por tamaño de venta
vol = df.groupby(["store_nbr", "family"], observed=True)["sales"].mean()
df["vol"] = pd.qcut(df.set_index(["store_nbr", "family"]).index.map(vol), 5,
                    labels=["q1 baja", "q2", "q3", "q4", "q5 alta"])
g = df.groupby("vol", observed=True).agg(rmsle=("se", r), sesgo=("e", "mean"), share=("se", "sum"))
g["share"] = 100 * g["share"] / TOT
print("\n## 1d. por volumen medio de la serie\n" + g.round(3).to_string())

# 2) Promo
train = pd.read_csv(ROOT / "data" / "train.csv", parse_dates=["date"], usecols=["date", "store_nbr", "family",
                                                                                 "sales", "onpromotion"])
df = df.merge(train[["date", "store_nbr", "family", "onpromotion"]], on=["date", "store_nbr", "family"], how="left")
df["promo"] = pd.cut(df["onpromotion"], [-1, 0, 5, 30, 1e9], labels=["0", "1-5", "6-30", ">30"])
g = df.groupby("promo", observed=True).agg(n=("se", "size"), rmsle=("se", r), sesgo=("e", "mean"),
                                           share=("se", "sum"))
g["share"] = 100 * g["share"] / TOT
print("\n## 2. por artículos en promo ese día\n" + g.round(3).to_string())

# 3) Familias: sesgo por fold (¿estable?)
fs = df.groupby(["family", "fold"], observed=True)["e"].mean().unstack().round(3)
fs["share"] = (100 * df.groupby("family", observed=True)["se"].sum() / TOT).round(2)
print("\n## 3. sesgo medio por familia y fold (top 12 por error)\n" + fs.sort_values("share", ascending=False)
      .head(12).to_string())
ts = df.groupby(["store_nbr", "fold"], observed=True)["e"].mean().unstack().round(3)
ts["absmax"] = ts.abs().max(axis=1)
print("\n## 3b. tiendas con mayor sesgo en algún fold\n" + ts.sort_values("absmax", ascending=False).head(8).to_string())

# 4) Ceros: real 0 y pred>0, ¿qué predice?
z = df[(df["sales"] == 0) & (df["pred"] > 0)]
print(f"\n## 4. real=0, pred>0: {len(z)} filas, {100 * z['se'].sum() / TOT:.1f}% del error;"
      f" pred mediana {z['pred'].median():.2f}, p90 {z['pred'].quantile(.9):.2f}")
zz = df.assign(z0=df["sales"] == 0)
zf = zz.groupby(["store_nbr", "family"], observed=True)["z0"].mean()
df["zrate"] = pd.cut(df.set_index(["store_nbr", "family"]).index.map(zf), [-.01, 0, .1, .3, .6, .99, 1],
                     labels=["0", "<10%", "10-30%", "30-60%", "60-99%", "100%"])
g = df.groupby("zrate", observed=True).agg(n=("se", "size"), rmsle=("se", r), sesgo=("e", "mean"),
                                           share=("se", "sum"))
g["share"] = 100 * g["share"] / TOT
print("  por fracción de ceros de la serie en la propia ventana (descriptivo, no usable)\n" + g.round(3).to_string())
# techo: en series intermitentes (10-99% ceros), sustituir pred por la mejor constante en log de la ventana
inter = df["zrate"].isin(["10-30%", "30-60%", "60-99%"])
best = df.groupby(["fold", "store_nbr", "family"], observed=True)["sales"].transform(lambda s: np.log1p(s).mean())
alt = df["se"].where(~inter, (best - np.log1p(df["sales"])) ** 2)
print(f"  techo: constante perfecta (en log) para intermitentes -> RMSLE {r(alt):.4f} (base {r(df['se']):.4f})")

# 5) Casos concretos con contexto
tr = train.set_index(["store_nbr", "family", "date"])["sales"].sort_index()
folds = df.groupby("fold")["date"].agg(["min", "max"])
cases = [(45, "SCHOOL AND OFFICE SUPPLIES", "f1"), (19, "GROCERY II", None), (35, "LIQUOR,WINE,BEER", None),
         (32, "CLEANING", None)]
for st, fam, fo in cases:
    c = df[(df["store_nbr"] == st) & (df["family"] == fam)]
    if fo is None:
        fo = c.groupby("fold")["se"].sum().idxmax()
    c = c[c["fold"] == fo]
    a, b = folds.loc[fo, "min"], folds.loc[fo, "max"]
    s = tr.loc[(st, fam)]
    prev = s[(s.index >= a - pd.Timedelta(days=28)) & (s.index < a)]
    ly = s[(s.index >= a - pd.Timedelta(days=364)) & (s.index <= b - pd.Timedelta(days=364))]
    print(f"\n## caso {st} × {fam} ({fo}, {a.date()}..{b.date()}): RMSLE {r(c['se']):.3f} sesgo {c['e'].mean():+.3f}")
    print(f"  28 d previos: {prev.values.astype(int).tolist()}")
    print(f"  mismo tramo -364 d: {ly.values.astype(int).tolist()}")
    print(f"  real: {c['sales'].values.astype(int).tolist()}")
    print(f"  pred: {c['pred'].round(1).tolist()}")
    print(f"  promo: {c['onpromotion'].astype(int).tolist()}")
    print(f"  sesgo por fold: {df[(df['store_nbr'] == st) & (df['family'] == fam)].groupby('fold')['e'].mean().round(2).to_dict()}")

# 6) GROCERY II: sesgo negativo sistemático. ¿Dónde?
g2 = df[df["family"] == "GROCERY II"]
print("\n## 6. GROCERY II: sesgo cuando real>0 vs real=0")
print(g2.assign(real0=g2["sales"] == 0).groupby("real0").agg(n=("se", "size"), sesgo=("e", "mean"),
                                                               rmsle=("se", r)).round(3).to_string())

# 7) Control c1 (vuelta al cole) si existe
try:
    c1 = load("preds-c1.csv.gz")
    print(f"\n## 7. control c1: RMSLE {r(c1['se']):.4f} sesgo {c1['e'].mean():+.4f}")
    g = c1.groupby("family").agg(rmsle=("se", r), sesgo=("e", "mean"), share=("se", "sum"))
    g["share"] = 100 * g["share"] / c1["se"].sum()
    print(g.sort_values("share", ascending=False).head(8).round(3).to_string())
except ValueError:
    pass
