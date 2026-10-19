"""V-004: LightGBM global directo (un modelo para las 1782 series) con rasgos de la fecha de corte.

Se apilan 8 cortes t_k = inicio_prediccion - 16 - 7k. Para cada corte y cada serie, rasgos calculados solo con dias < t_k:
media de log1p a 3/7/14/28/56 d y perfil semanal log (8 sem) del dia objetivo; mas h (1..16), dow, store_nbr, family.
Objetivo log1p(ventas) en t_k+h-1, L2. Sin promos/festivos/anual. Prediccion expm1 clip 0.

Contrato (lo llama scripts/backtest.py y scripts/make_submission.py):
    fit_predict(history, future, ctx) -> array de predicciones (>= 0), una por fila de `future`, en el mismo orden.
"""
import numpy as np
import pandas as pd
import lightgbm as lgb

HORIZON = 16
N_CUTS = 8
WINDOWS = (3, 7, 14, 28, 56)
PROFILE_DAYS = 56
PARAMS = dict(objective="regression", learning_rate=0.05, num_leaves=31, min_data_in_leaf=50,
              feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, lambda_l2=0.1,
              verbose=-1, num_threads=4)
ROUNDS = 400


def _features(M, origin, dow0, n_series):
    """M: (series, dias) log1p; origin: columna del primer dia a predecir. Rasgos (series, 16) con datos < origin."""
    past = M[:, origin - PROFILE_DAYS:origin]
    feats = {}
    for w in WINDOWS:
        feats[f"m{w}"] = np.repeat(past[:, -w:].mean(1, keepdims=True), HORIZON, 1)
    base = past.mean(1)
    off = np.zeros((n_series, 7))
    for d in range(7):
        idx = [j for j in range(PROFILE_DAYS) if (dow0 - PROFILE_DAYS + j) % 7 == d]
        off[:, d] = past[:, idx].mean(1) - base
    dows = (dow0 + np.arange(HORIZON)) % 7
    feats["prof"] = off[:, dows]
    feats["h"] = np.tile(np.arange(1, HORIZON + 1), (n_series, 1)).astype(float)
    feats["dow"] = np.tile(dows, (n_series, 1)).astype(float)
    return feats


def fit_predict(history, future, ctx):
    keys = ["store_nbr", "family"]
    start = history["date"].max() + np.timedelta64(1, "D")
    days = pd.date_range(history["date"].min(), history["date"].max())
    h = history.assign(ls=np.log1p(history["sales"]))
    piv = h.pivot_table(index=keys, columns="date", values="ls", aggfunc="sum", observed=True)
    piv = piv.reindex(columns=days).fillna(0.0)
    series = piv.index.to_frame(index=False)
    M = piv.to_numpy()
    n = len(series)
    T = M.shape[1]
    store = np.repeat(series["store_nbr"].to_numpy().astype(int)[:, None], HORIZON, 1)
    fam = np.repeat(pd.Categorical(series["family"].astype(str)).codes[:, None], HORIZON, 1)

    def build(origin, dow0, with_y):
        f = _features(M, origin, dow0, n)
        f["store_nbr"] = store
        f["family"] = fam
        X = pd.DataFrame({k: v.ravel() for k, v in f.items()})
        y = M[:, origin:origin + HORIZON].ravel() if with_y else None
        return X, y

    Xs, ys = [], []
    for k in range(N_CUTS):
        o = T - HORIZON - 7 * k
        if o - PROFILE_DAYS < 0:
            break
        dow0 = (start.dayofweek - HORIZON - 7 * k) % 7
        X, y = build(o, dow0, True)
        Xs.append(X)
        ys.append(y)
    X = pd.concat(Xs, ignore_index=True)
    y = np.concatenate(ys)
    ds = lgb.Dataset(X, y, categorical_feature=["store_nbr", "family"])
    model = lgb.train({**PARAMS, "seed": int(ctx.get("seed", 0) or 0)}, ds, num_boost_round=ROUNDS)

    Xp, _ = build(T, start.dayofweek, False)
    pred = model.predict(Xp).reshape(n, HORIZON)
    fdates = pd.date_range(start, periods=HORIZON)
    lookup = pd.DataFrame(pred, index=pd.MultiIndex.from_frame(series), columns=fdates).stack()
    lookup.index.names = keys + ["date"]
    fut = future[keys + ["date"]].copy()
    fut["family"] = fut["family"].astype(str)
    lookup = lookup.rename("p").reset_index()
    lookup["family"] = lookup["family"].astype(str)
    merged = fut.merge(lookup, on=keys + ["date"], how="left")
    return np.expm1(merged["p"].fillna(0.0).to_numpy()).clip(min=0)
