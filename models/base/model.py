"""Base v0: media de las ventas de los últimos 14 días de cada tienda×familia.

Es la línea base más sencilla que tiene sentido: no sabe nada de días de la semana, festivos ni promociones.
Todo lo que venga después tiene que ganarle; si no, no aporta.

Contrato (lo llama scripts/backtest.py y scripts/make_submission.py):
    fit_predict(history, future, ctx) -> array de predicciones (>= 0), una por fila de `future`, en el mismo orden.
    - history: ventas ANTERIORES a la fecha de corte (id, date, store_nbr, family, sales, onpromotion)
    - future: los 16 días a predecir, sin `sales` (id, date, store_nbr, family, onpromotion)
    - ctx: tablas auxiliares {"oil", "holidays", "stores", "transactions"} (transactions solo hasta el corte) y "seed"
"""
import numpy as np

WINDOW_DAYS = 14
PROFILE_WEEKS = 8


def fit_predict(history, future, ctx):
    cutoff = history["date"].max()
    recent = history[history["date"] > cutoff - np.timedelta64(WINDOW_DAYS, "D")]
    mean = recent.groupby(["store_nbr", "family"], observed=True)["sales"].mean().rename("pred")
    out = future.join(mean, on=["store_nbr", "family"])

    # Factor del día de la semana por tienda×familia (últimas 8 semanas): media del día / media global.
    wk = history[history["date"] > cutoff - np.timedelta64(PROFILE_WEEKS * 7, "D")].copy()
    wk["dow"] = wk["date"].dt.dayofweek
    keys = ["store_nbr", "family"]
    dow_mean = wk.groupby(keys + ["dow"], observed=True)["sales"].mean().rename("dm").reset_index()
    all_mean = wk.groupby(keys, observed=True)["sales"].mean().rename("am").reset_index()
    fac = dow_mean.merge(all_mean, on=keys)
    fac["factor"] = np.where(fac["am"] > 0, fac["dm"] / fac["am"].where(fac["am"] > 0, 1), 1.0)
    out["dow"] = out["date"].dt.dayofweek
    out = out.join(fac.set_index(keys + ["dow"])["factor"], on=keys + ["dow"])
    factor = out["factor"].fillna(1.0)
    return (out["pred"].fillna(0) * factor).clip(lower=0).to_numpy()
