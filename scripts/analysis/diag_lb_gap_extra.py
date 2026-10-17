"""T-027 · complemento: (a) qué familias explican la diferencia v2/v3 el 16-ago-2017 (día 1 del test);
(b) resumen del ruido entre ventanas guardado por diag_lb_gap.py (sin reentrenar).

  python scripts/analysis/diag_lb_gap_extra.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from backtest import DATA  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    test = pd.read_csv(DATA / "test.csv", parse_dates=["date"])
    a = pd.read_csv(ROOT / "dist" / "submission-base-v2.csv").rename(columns={"sales": "v2"})
    b = pd.read_csv(ROOT / "dist" / "submission-base-v3.csv").rename(columns={"sales": "v3"})
    d = test.merge(a, on="id").merge(b, on="id")
    d["dl"] = np.log1p(d.v3) - np.log1p(d.v2)
    d1 = d[d.date == "2017-08-16"]
    tot = (d1.dl ** 2).sum()
    print("16-ago: familias con más diferencia v3-v2 (share de Σ Δlog²)")
    g = d1.groupby("family").agg(media=("dl", "mean"), share=("dl", lambda x: (x ** 2).sum() / tot),
                                 v2_cero=("v2", lambda x: (x == 0).mean()), v3_cero=("v3", lambda x: (x == 0).mean()))
    print(g.sort_values("share", ascending=False).head(8).round(3).to_string())
    print(f"ceros predichos el 16-ago: v2 {(d1.v2 == 0).mean():.1%} v3 {(d1.v3 == 0).mean():.1%}; "
          f"resto de días: v2 {(d[d.date > '2017-08-16'].v2 == 0).mean():.1%} v3 {(d[d.date > '2017-08-16'].v3 == 0).mean():.1%}")
    tr = pd.read_csv(DATA / "train.csv", usecols=["date", "sales"], parse_dates=["date"])
    z = tr[tr.date.isin(pd.to_datetime(["2016-08-16", "2016-08-17", "2017-08-15"]))]
    print("ceros reales en train:", z.groupby("date").sales.apply(lambda x: f"{(x == 0).mean():.1%}").to_dict())

    t = pd.read_csv(ROOT / "scripts" / "analysis" / "diag_lb_gap_windows.csv")
    print(f"\nventanas={len(t)} · v3 RMSLE media {t.v3.mean():.3f} std {t.v3.std():.3f} "
          f"(mediana {t.v3.median():.3f}, p10-p90 {t.v3.quantile(.1):.3f}-{t.v3.quantile(.9):.3f})")
    print(f"Δ(v3−v2) mediana {t['diff'].median():+.4f} · p10-p90 {t['diff'].quantile(.1):+.4f}..{t['diff'].quantile(.9):+.4f} "
          f"· ventanas con Δ > −0.005: {(t['diff'] > -0.005).sum()}/{len(t)} · con Δ > −0.015: {(t['diff'] > -0.015).sum()}/{len(t)}")
    ag = t[t.start.str.startswith("2016-08")]
    print("ventanas de agosto 2016:\n", ag[["start", "v2", "v3", "diff"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
