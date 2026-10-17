"""T-027 · ¿Por qué base-v3 mejora −0.025 en CV y solo −0.001 en Kaggle?

  python scripts/analysis/diag_lb_gap.py            # todo (bug, diff test, ruido)
  python scripts/analysis/diag_lb_gap.py --skip-noise

(1) Ruta de envío: integridad de test.csv/dist y reproducción de make_submission en la ventana del holdout
    (solo se compara predicción contra predicción, NO se mira la venta real del holdout).
(2) Dónde difieren v2 (variants/V-002) y v3 (models/base) en las predicciones del test de Kaggle.
(3) Ruido: RMSLE de v2 y v3 en muchas ventanas de 16 días anteriores a los folds.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from backtest import DATA, load_data, load_model, split  # noqa: E402

V2, V3 = ROOT / "variants" / "V-002", ROOT / "models" / "base"
KEYS = ["date", "store_nbr", "family"]


def rmsle(y, p):
    return float(np.sqrt(np.mean((np.log1p(np.clip(p, 0, None)) - np.log1p(y)) ** 2)))


def part1(train, ctx):
    print("\n=== (1) Ruta de envío ===")
    test = pd.read_csv(DATA / "test.csv", parse_dates=["date"], dtype={"family": "category"})
    print(f"test: {len(test)} filas, {test.date.min().date()}..{test.date.max().date()}, "
          f"ids únicos={test.id.is_unique}, ids crecientes={test.id.is_monotonic_increasing}")
    print("familias test == train:", set(test.family.astype(str)) == set(train.family.astype(str)),
          "| categorías en el mismo orden:", list(test.family.cat.categories) == list(train.family.cat.categories))
    print("tiendas test == train:", set(test.store_nbr) == set(train.store_nbr))
    last = train[train.date == train.date.max()]
    print(f"último día de train {train.date.max().date()}: {len(last)} series (esperado 1782)")
    for v in ("base-v2", "base-v3"):
        d = pd.read_csv(ROOT / "dist" / f"submission-{v}.csv")
        print(f"dist {v}: filas={len(d)} mismos ids y orden={d.id.equals(test.id)} NaN={d.sales.isna().sum()} "
              f"ceros={np.mean(d.sales == 0):.1%}")
    # promos del test frente a los 16 días anteriores (v3 usa promo_day)
    prev = train[train.date > train.date.max() - pd.Timedelta(days=16)]
    print(f"onpromotion medio: test {test.onpromotion.mean():.2f} · últimos 16 d de train {prev.onpromotion.mean():.2f} "
          f"· máx test {test.onpromotion.max()} vs train {train.onpromotion.max()}")

    # Reproducir make_submission cortando en 2017-07-31: future con id, orden de columnas y dtype como test.csv
    hist, fut, _, c = split(train, ctx, "2017-07-31", "2017-08-15")
    fut = fut.sample(frac=1, random_state=0).reset_index(drop=True)  # orden distinto: el merge debe aguantarlo
    fut = fut[["id", "date", "store_nbr", "family", "onpromotion"]]
    fut["family"] = fut["family"].astype(str).astype("category")
    p = np.clip(load_model(V3).fit_predict(hist, fut, {**c, "seed": 42}), 0, None)
    ref = pd.read_csv(ROOT / "eval" / "results" / "base-v3-holdout" / "preds-holdout.csv.gz", parse_dates=["date"])
    m = fut[KEYS].assign(p=p).merge(ref[KEYS + ["pred"]].assign(family=lambda x: x.family.astype(str)).rename(
        columns={"pred": "ref"}), on=KEYS, how="left")
    dl = np.abs(np.log1p(m.p) - np.log1p(m.ref))
    print(f"ruta envío vs backtest (holdout, solo preds): filas sin pareja={m.ref.isna().sum()}, "
          f"|Δlog| máx={dl.max():.2e}, medio={dl.mean():.2e}")


def part2(train):
    print("\n=== (2) v2 vs v3 en el test de Kaggle ===")
    test = pd.read_csv(DATA / "test.csv", parse_dates=["date"])
    a = pd.read_csv(ROOT / "dist" / "submission-base-v2.csv").rename(columns={"sales": "v2"})
    b = pd.read_csv(ROOT / "dist" / "submission-base-v3.csv").rename(columns={"sales": "v3"})
    d = test.merge(a, on="id").merge(b, on="id")
    d["dl"] = np.log1p(d.v3) - np.log1p(d.v2)
    tot = (d.dl ** 2).sum()
    print(f"RMS(Δlog v3−v2) global = {np.sqrt((d.dl ** 2).mean()):.3f} · media Δlog = {d.dl.mean():+.3f}")
    g = d.groupby("family").agg(media=("dl", "mean"), rms=("dl", lambda x: np.sqrt((x ** 2).mean())),
                                share=("dl", lambda x: (x ** 2).sum() / tot))
    print(g.sort_values("share", ascending=False).head(10).round(3).to_string())
    print("\npor día:")
    print(d.groupby(d.date.dt.strftime("%m-%d %a")).dl.agg(
        media="mean", rms=lambda x: np.sqrt((x ** 2).mean())).round(3).T.to_string())
    # SCHOOL: nivel predicho vs lo que pasó el año anterior en las mismas fechas (2016-08-16..31) y justo antes
    s = d[d.family == "SCHOOL AND OFFICE SUPPLIES"]
    tr = train[train.family == "SCHOOL AND OFFICE SUPPLIES"]
    def lvl(lo, hi):
        w = tr[(tr.date >= lo) & (tr.date <= hi)]
        return np.expm1(np.log1p(w.sales).mean())
    print(f"\nSCHOOL nivel (media geométrica por fila): v2 {np.expm1(np.log1p(s.v2).mean()):.1f} · "
          f"v3 {np.expm1(np.log1p(s.v3).mean()):.1f} · real 2016-08-16..31 {lvl('2016-08-16', '2016-08-31'):.1f} · "
          f"real 2016-07-31..08-15 {lvl('2016-07-31', '2016-08-15'):.1f} · real 2016-09-01..16 {lvl('2016-09-01', '2016-09-16'):.1f}")
    print("SCHOOL por día (suma de unidades, todas las tiendas):")
    t16 = tr[(tr.date >= "2016-07-20") & (tr.date <= "2016-09-20")].groupby("date").sales.sum()
    print("  2016:", " ".join(f"{k:%m-%d}:{v:.0f}" for k, v in t16.items() if k.day in (1, 8, 16, 24, 31) or k.day == 20))
    print("  test v2:", " ".join(f"{k:%m-%d}:{v:.0f}" for k, v in s.groupby("date").v2.sum().items() if k.day in (16, 24, 31)),
          " v3:", " ".join(f"{k:%m-%d}:{v:.0f}" for k, v in s.groupby("date").v3.sum().items() if k.day in (16, 24, 31)))


def part3(train, ctx):
    print("\n=== (3) Ruido entre ventanas de 16 días (v2 y v3 reentrenados en cada una) ===")
    starts = list(pd.date_range("2016-06-01", "2017-05-12", freq="16D")) + [pd.Timestamp("2016-08-16")]
    m2, m3 = load_model(V2), load_model(V3)
    rows = []
    for s in sorted(set(starts)):
        e = s + pd.Timedelta(days=15)
        h, f, y, c = split(train, ctx, s, e)
        c["seed"] = 42
        p2, p3 = m2.fit_predict(h, f, c), m3.fit_predict(h, f, c)
        ns = f.family.astype(str) != "SCHOOL AND OFFICE SUPPLIES"
        r = dict(start=s.date(), v2=rmsle(y, p2), v3=rmsle(y, p3),
                 v2_noschool=rmsle(y[ns], np.asarray(p2)[ns]), v3_noschool=rmsle(y[ns], np.asarray(p3)[ns]))
        r["diff"] = r["v3"] - r["v2"]
        rows.append(r)
        print(f"  {s.date()}  v2 {r['v2']:.4f}  v3 {r['v3']:.4f}  Δ {r['diff']:+.4f}  "
              f"(sin SCHOOL Δ {r['v3_noschool'] - r['v2_noschool']:+.4f})", flush=True)
    t = pd.DataFrame(rows)
    out = ROOT / "scripts" / "analysis" / "diag_lb_gap_windows.csv"
    t.to_csv(out, index=False)
    print(f"\nv3 RMSLE entre ventanas: media {t.v3.mean():.4f} · std {t.v3.std():.4f} · min {t.v3.min():.4f} · max {t.v3.max():.4f}")
    print(f"Δ(v3−v2): media {t['diff'].mean():+.4f} · std {t['diff'].std():.4f} · peor {t['diff'].max():+.4f} · "
          f"ventanas con Δ > −0.005: {(t['diff'] > -0.005).sum()}/{len(t)}")
    print(f"guardado {out.relative_to(ROOT).as_posix()}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-noise", action="store_true")
    ap.add_argument("--only-noise", action="store_true")
    o = ap.parse_args()
    train, ctx = load_data()
    if not o.only_noise:
        part1(train, ctx)
        part2(train)
    if not o.skip_noise:
        part3(train, ctx)


if __name__ == "__main__":
    main()
