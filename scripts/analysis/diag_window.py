"""T-027 · Desglose v2 vs v3 en una ventana de 16 días (dónde gana/pierde v3), por día y familia.

  python scripts/analysis/diag_window.py 2017-02-28
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from backtest import load_data, load_model, split  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    s = pd.Timestamp(sys.argv[1])
    train, ctx = load_data()
    h, f, y, c = split(train, ctx, s, s + pd.Timedelta(days=15))
    c["seed"] = 42
    p2 = np.clip(load_model(ROOT / "variants" / "V-002").fit_predict(h, f, c), 0, None)
    p3 = np.clip(load_model(ROOT / "models" / "base").fit_predict(h, f, c), 0, None)
    d = f[["date", "store_nbr", "family"]].assign(y=np.asarray(y), e2=(np.log1p(p2) - np.log1p(y)) ** 2,
                                                  e3=(np.log1p(p3) - np.log1p(y)) ** 2, b3=np.log1p(p3) - np.log1p(y))
    n = len(d)
    d["dmse"] = (d.e3 - d.e2) / n  # aporte de cada fila a MSE(v3) − MSE(v2)
    print(f"RMSLE v2 {np.sqrt(d.e2.mean()):.4f} v3 {np.sqrt(d.e3.mean()):.4f}")
    print("\npor día (aporte a ΔMSE, sesgo v3, % ventas cero):")
    print(d.groupby(d.date.dt.strftime("%m-%d %a")).agg(dmse=("dmse", "sum"), sesgo_v3=("b3", "mean"),
                                                        ceros=("y", lambda v: (v == 0).mean())).round(4).T.to_string())
    print("\nfamilias que más empeoran con v3:")
    print(d.groupby("family", observed=True).dmse.sum().sort_values().tail(5).round(4).to_string())
    print("\ntiendas que más empeoran con v3:")
    print(d.groupby("store_nbr").agg(dmse=("dmse", "sum"), ceros=("y", lambda v: (v == 0).mean()))
          .sort_values("dmse").tail(5).round(4).to_string())


if __name__ == "__main__":
    main()
