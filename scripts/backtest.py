"""Backtest fijo: mide un modelo con validación temporal (folds de eval/folds.json). CPU, determinista por semilla.

  python scripts/backtest.py --src models/base --name base-v0          # 4 folds → eval/results/base-v0.json
  python scripts/backtest.py --src variants/V-001 --name V-001 --quick # solo f1, para comprobar que corre
  python scripts/backtest.py --src models/base --name base-v0-holdout --holdout   # SOLO el consultor

Para cada fold: el modelo recibe las ventas anteriores a `start` (history) y las filas de los 16 días (future) sin ventas.
Nunca ve el futuro: así se mide lo que pasaría de verdad en el test de Kaggle.
Salida: eval/results/<name>.json (resumen, en git) y eval/results/<name>/preds-<fold>.csv.gz (predicciones, fuera de git).
"""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "eval" / "results"


def rmsle(y, p):
    """Error cuadrático medio de los logaritmos: castiga igual equivocarse un 20 % en 10 que en 10.000 unidades."""
    y, p = np.asarray(y, float), np.clip(np.asarray(p, float), 0, None)
    return float(np.sqrt(np.mean((np.log1p(p) - np.log1p(y)) ** 2)))


def load_data(data_dir=DATA):
    if not (data_dir / "train.csv").exists():
        sys.exit(f"Faltan los datos en {data_dir} (train.csv…). Ver README «Cómo reproducirlo».")
    train = pd.read_csv(data_dir / "train.csv", parse_dates=["date"], dtype={"family": "category"})
    ctx = {"oil": pd.read_csv(data_dir / "oil.csv", parse_dates=["date"]),
           "holidays": pd.read_csv(data_dir / "holidays_events.csv", parse_dates=["date"]),
           "stores": pd.read_csv(data_dir / "stores.csv"),
           "transactions": pd.read_csv(data_dir / "transactions.csv", parse_dates=["date"])}
    return train, ctx


def load_model(src):
    f = Path(src) / "model.py"
    spec = importlib.util.spec_from_file_location(f"model_{Path(src).name}", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def split(train, ctx, start, end):
    """history = todo lo anterior a start; future = [start, end] sin ventas. ctx filtrado sin fugas."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    history = train[train["date"] < start].copy()
    window = train[(train["date"] >= start) & (train["date"] <= end)]
    future, y = window.drop(columns=["sales"]).reset_index(drop=True), window["sales"].to_numpy()
    c = dict(ctx)
    c["transactions"] = ctx["transactions"][ctx["transactions"]["date"] < start]  # en el test no se conocen
    return history, future, y, c


def run(src, name, folds, train, ctx, seed=42, save_preds=True):
    model = load_model(src)
    out_dir = RESULTS / name
    out_dir.mkdir(parents=True, exist_ok=True)
    res = []
    for f in folds:
        history, future, y, c = split(train, ctx, f["start"], f["end"])
        c["seed"] = seed
        t0 = time.time()
        p = np.asarray(model.fit_predict(history, future, c), float)
        secs = time.time() - t0
        assert len(p) == len(future), f"{f['id']}: {len(p)} predicciones para {len(future)} filas"
        assert np.isfinite(p).all(), f"{f['id']}: predicciones con NaN/inf"
        df = future[["date", "store_nbr", "family"]].assign(sales=y, pred=np.clip(p, 0, None))
        if save_preds:
            df.to_csv(out_dir / f"preds-{f['id']}.csv.gz", index=False)
        le = (np.log1p(df["pred"]) - np.log1p(df["sales"])) ** 2
        res.append(dict(id=f["id"], start=f["start"], end=f["end"], rmsle=rmsle(y, p), secs=round(secs, 1),
                        by_family={k: float(np.sqrt(v)) for k, v in le.groupby(df["family"], observed=True).mean().items()},
                        bias=float((np.log1p(df["pred"]) - np.log1p(df["sales"])).mean())))
        print(f"  {f['id']} {f['start']}..{f['end']}  RMSLE {res[-1]['rmsle']:.4f}  ({secs:.1f} s)")
    scores = [r["rmsle"] for r in res]
    summary = dict(name=name, src=str(Path(src).as_posix()), seed=seed, folds=res,
                   mean=float(np.mean(scores)), std=float(np.std(scores)), secs=round(sum(r["secs"] for r in res), 1))
    (RESULTS / f"{name}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return summary


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="carpeta con model.py (models/base o variants/V-xxx)")
    ap.add_argument("--name", help="nombre del resultado (por defecto, el de la carpeta)")
    ap.add_argument("--quick", action="store_true", help="solo el fold más reciente (comprobar que corre)")
    ap.add_argument("--holdout", action="store_true", help="evalúa en el holdout (SOLO el consultor, antes de enviar)")
    ap.add_argument("--seed", type=int, default=42)
    o = ap.parse_args(argv)
    spec = json.loads((ROOT / "eval" / ("holdout.json" if o.holdout else "folds.json")).read_text(encoding="utf-8"))
    folds = spec["folds"][:1] if o.quick else spec["folds"]
    name = o.name or Path(o.src).name
    name += "-quick" if o.quick else ""
    train, ctx = load_data()
    print(f"{name}: {o.src} · {len(folds)} fold(s) · semilla {o.seed}")
    s = run(o.src, name, folds, train, ctx, o.seed)
    print(f"CV RMSLE {s['mean']:.4f} ± {s['std']:.4f} · {s['secs']:.0f} s → eval/results/{name}.json")


if __name__ == "__main__":
    main()
