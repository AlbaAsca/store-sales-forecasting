"""V-002: media de 14 días y perfil semanal en escala log (la de la métrica RMSLE).

pred = expm1( media(log1p ventas, 14 d) + [media(log1p del día de la semana) - media(log1p), 8 semanas] ), >= 0.

Contrato (lo llama scripts/backtest.py y scripts/make_submission.py):
    fit_predict(history, future, ctx) -> array de predicciones (>= 0), una por fila de `future`, en el mismo orden.
    - history: ventas ANTERIORES a la fecha de corte (id, date, store_nbr, family, sales, onpromotion)
    - future: los 16 días a predecir, sin `sales` (id, date, store_nbr, family, onpromotion)
    - ctx: tablas auxiliares {"oil", "holidays", "stores", "transactions"} y "seed"
"""
import numpy as np

WINDOW_DAYS = 14
PROFILE_WEEKS = 8


def fit_predict(history, future, ctx):
    cutoff = history["date"].max()
    keys = ["store_nbr", "family"]
    h = history[history["date"] > cutoff - np.timedelta64(PROFILE_WEEKS * 7, "D")][keys + ["date", "sales"]].copy()
    h["ls"] = np.log1p(h["sales"])

    recent = h[h["date"] > cutoff - np.timedelta64(WINDOW_DAYS, "D")]
    level = recent.groupby(keys, observed=True)["ls"].mean().rename("level")

    h["dow"] = h["date"].dt.dayofweek
    dow_mean = h.groupby(keys + ["dow"], observed=True)["ls"].mean().rename("dm")
    all_mean = h.groupby(keys, observed=True)["ls"].mean().rename("am")
    prof = dow_mean.reset_index().merge(all_mean.reset_index(), on=keys)
    prof["off"] = prof["dm"] - prof["am"]

    out = future[keys + ["date"]].copy()
    out["dow"] = out["date"].dt.dayofweek
    out = out.join(level, on=keys)
    out = out.join(prof.set_index(keys + ["dow"])["off"], on=keys + ["dow"])
    logpred = out["level"].fillna(0) + out["off"].fillna(0)
    return np.expm1(logpred).clip(lower=0).to_numpy()
