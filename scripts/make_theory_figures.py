"""Una gráfica antes/después por cada base aprobada → docs/img/teorias/base-vN.png (+ eval/theory_figures.json).

Para base-vN compara la base anterior (tag base-v(N-1)) con la nueva (tag base-vN) en el mismo fold de validación
(por defecto el más reciente de eval/folds.json; nunca el holdout), semilla 42, y dibuja la serie tienda×familia donde más
baja el error. Coste: ~9 predicciones de un fold (base-v0..v9, una vez cada una; se cachean en eval/tmp/).

  python scripts/make_theory_figures.py              # todas (base-v1..base-v9)
  python scripts/make_theory_figures.py --only 6     # solo base-v6
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
TMP = ROOT / "eval" / "tmp" / "theory"
IMG = ROOT / "docs" / "img" / "teorias"
CLOSED = (18, 25, 52)
TITLES = {
    1: "base-v1: el perfil de cada día de la semana",
    2: "base-v2: perfil de la semana en escala logarítmica",
    3: "base-v3: un modelo global que aprende de todas las series",
    4: "base-v4: promediar la predicción directa y la recursiva",
    5: "base-v5: el modelo global afinado",
    6: "base-v6: el año anterior sin cierres",
    7: "base-v7: combinar las mejoras del año anterior y de la estacionalidad",
    8: "base-v8: promociones de los días vecinos",
    9: "base-v9: promedio de tres historiales (corto, medio y largo)",
}


def rmsle(y, p):
    y, p = np.asarray(y, float), np.clip(np.asarray(p, float), 0, None)
    return float(np.sqrt(np.mean((np.log1p(p) - np.log1p(y)) ** 2)))


def pick_series(df, min_mean=5.0, exclude=CLOSED):
    """Función pura. df: columnas store_nbr, family, sales, before, after (una fila por día y serie).
    Devuelve (store, family, rmsle_antes, rmsle_despues) de la serie con mayor bajada de error (antes − después),
    con ventas medias >= min_mean y sin las tiendas `exclude`. None si no hay candidata."""
    d = df[~df["store_nbr"].isin(exclude)]
    best = None
    for (s, f), g in d.groupby(["store_nbr", "family"], observed=True):
        if g["sales"].mean() < min_mean:
            continue
        b, a = rmsle(g["sales"], g["before"]), rmsle(g["sales"], g["after"])
        if best is None or b - a > best[2] - best[3]:
            best = (int(s), str(f), b, a)
    return best


def git_model(tag, dest):
    """Escribe models/base/model.py tal como estaba en `tag` (git show, sin tocar el árbol de trabajo)."""
    out = subprocess.run(["git", "show", f"{tag}:models/base/model.py"], cwd=ROOT, capture_output=True, check=True).stdout
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "model.py").write_bytes(out)
    return dest


def predict(tag, fold, train, ctx, seed=42):
    """Predicciones del tag en el fold (cacheadas en eval/tmp/theory)."""
    import backtest as bt
    cache = TMP / f"{tag}-{fold['id']}-s{seed}.csv.gz"
    if cache.exists():
        return pd.read_csv(cache, parse_dates=["date"])
    model = bt.load_model(git_model(tag, TMP / tag))
    history, future, y, c = bt.split(train, ctx, fold["start"], fold["end"])
    c["seed"] = seed
    p = np.clip(np.asarray(model.fit_predict(history, future, c), float), 0, None)
    df = future[["date", "store_nbr", "family"]].assign(sales=y, pred=p)
    df["family"] = df["family"].astype(str)
    df.to_csv(cache, index=False)
    return df


def draw(n, row, df, train, fold, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    s, f = row["store"], row["family"]
    h = train[(train["store_nbr"] == s) & (train["family"].astype(str) == f)]
    start = pd.Timestamp(fold["start"])
    h = h[(h["date"] >= start - pd.Timedelta(weeks=5)) & (h["date"] < start)]
    g = df[(df["store_nbr"] == s) & (df["family"] == f)].sort_values("date")
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(h["date"], h["sales"], color="black", lw=1.4)
    ax.plot(g["date"], g["sales"], color="black", lw=2, label="ventas reales")
    ax.plot(g["date"], g["before"], color="#9ca3af", ls="--", lw=2, label=f"antes (base-v{n-1}): error {row['rmsle_before']:.2f}")
    ax.plot(g["date"], g["after"], color="#2563eb", lw=2.2, label=f"después (base-v{n}): error {row['rmsle_after']:.2f}")
    ax.axvline(start - pd.Timedelta(hours=12), color="#d1d5db", lw=1)
    ax.set_title(f"{TITLES[n]}\ntienda {s} · {f.lower()}", fontsize=11)
    ax.set_ylabel("unidades vendidas al día")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="best")
    fig.autofmt_xdate()
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, help="solo base-vN")
    ap.add_argument("--fold", default=None, help="id del fold (por defecto el más reciente de folds.json)")
    ap.add_argument("--seed", type=int, default=42)
    o = ap.parse_args(argv)
    import backtest as bt
    folds = json.loads((ROOT / "eval" / "folds.json").read_text(encoding="utf-8"))["folds"]
    fold = next(x for x in folds if x["id"] == o.fold) if o.fold else folds[0]
    train, ctx = bt.load_data()
    TMP.mkdir(parents=True, exist_ok=True)
    meta_path = ROOT / "eval" / "theory_figures.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    for n in ([o.only] if o.only else range(1, 10)):
        print(f"base-v{n}…")
        b, a = predict(f"base-v{n-1}", fold, train, ctx, o.seed), predict(f"base-v{n}", fold, train, ctx, o.seed)
        df = b.rename(columns={"pred": "before"}).assign(after=a["pred"].to_numpy())
        assert (b[["date", "store_nbr"]].values == a[["date", "store_nbr"]].values).all()
        best = pick_series(df)
        if best is None:
            print("  sin serie candidata")
            continue
        s, f, rb, ra = best
        row = dict(store=s, family=f, rmsle_before=rb, rmsle_after=ra, fold=fold["id"], seed=o.seed,
                   rmsle_fold_before=rmsle(df["sales"], df["before"]), rmsle_fold_after=rmsle(df["sales"], df["after"]))
        draw(n, row, df, train, fold, IMG / f"base-v{n}.png")
        meta[f"base-v{n}"] = row
        print(f"  tienda {s} {f}: {rb:.3f} → {ra:.3f}")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
