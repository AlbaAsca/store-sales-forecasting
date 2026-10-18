"""Sesgo por fecha concreta (todas las series juntas) y cuánto error quitaría corregirlo.

Uso: python scripts/analysis/errors_daybias.py V-038 [V-038-s7]
Si el sesgo de un día es común a todas las series (p. ej. un día de compras raro), aparece aquí;
el contrafactual «restar el sesgo medio del día» es un techo (usa el futuro), no una mejora alcanzable.
"""
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

for run in sys.argv[1:]:
    parts = [pd.read_csv(f"eval/results/{run}/preds-f{i}.csv.gz").assign(fold=f"f{i}") for i in range(1, 5)]
    d = pd.concat(parts)
    d["e"] = np.log1p(d.pred.clip(lower=0)) - np.log1p(d.sales)
    d = d[d.sales.notna()]
    base = np.sqrt((d.e ** 2).mean())
    g = d.groupby(["fold", "date"]).e.agg(["mean", lambda x: np.sqrt((x ** 2).mean())])
    g.columns = ["sesgo", "rmsle"]
    g["dow"] = pd.to_datetime(g.index.get_level_values("date")).day_name().str[:3]
    print(f"\n=== {run}: RMSLE {base:.4f}")
    print(g.round(3).to_string())
    adj = d.e - d.groupby(["fold", "date"]).e.transform("mean")
    print(f"techo quitando sesgo por día (fuga): {np.sqrt((adj ** 2).mean()):.4f}")
    # mismo, pero el sesgo del día calculado solo con series grandes (¿es un efecto de demanda o de las pequeñas?)
    vol = d.groupby(["store_nbr", "family"]).sales.transform("mean")
    big = vol >= vol.quantile(0.6)
    print("sesgo por día, series grandes vs pequeñas (corr):",
          round(d[big].groupby(["fold", "date"]).e.mean().corr(d[~big].groupby(["fold", "date"]).e.mean()), 2))
