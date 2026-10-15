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


def fit_predict(history, future, ctx):
    cutoff = history["date"].max()
    recent = history[history["date"] > cutoff - np.timedelta64(WINDOW_DAYS, "D")]
    mean = recent.groupby(["store_nbr", "family"], observed=True)["sales"].mean().rename("pred")
    out = future.join(mean, on=["store_nbr", "family"])
    return out["pred"].fillna(0).clip(lower=0).to_numpy()
