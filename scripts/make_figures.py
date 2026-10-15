"""Figuras del README → docs/img/*.png. Las conceptuales no necesitan datos; las de datos se saltan si falta data/.

  python scripts/make_figures.py            # todas las que se puedan
  python scripts/make_figures.py --only progreso
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "img"
DATA = ROOT / "data"
INK, MUTED, ACCENT, WARN, OK = "#1f2937", "#9ca3af", "#2563eb", "#dc2626", "#16a34a"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "figure.dpi": 110, "savefig.bbox": "tight"})


def save(fig, name):
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMG / f"{name}.png")
    plt.close(fig)
    print(f"  docs/img/{name}.png")


def backtest():
    """Línea de tiempo: dónde caen los 4 folds, el holdout y el test de Kaggle."""
    folds = json.loads((ROOT / "eval" / "folds.json").read_text(encoding="utf-8"))["folds"]
    hold = json.loads((ROOT / "eval" / "holdout.json").read_text(encoding="utf-8"))["folds"][0]
    rows = [(f["id"], f["start"], f["end"], ACCENT) for f in reversed(folds)]
    rows += [("holdout", hold["start"], hold["end"], WARN), ("test Kaggle", "2017-08-16", "2017-08-31", INK)]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    t0 = pd.Timestamp("2017-04-20")
    for i, (name, s, e, col) in enumerate(rows):
        s, e = pd.Timestamp(s), pd.Timestamp(e)
        if col == ACCENT:
            ax.barh(i, (s - t0).days, left=t0, color="#dbeafe", height=0.55)
            ax.text(t0 + (s - t0) / 2, i, "entrena con el pasado", ha="center", va="center", fontsize=9, color=ACCENT)
        ax.barh(i, (e - s).days + 1, left=s, color=col, height=0.55)
        ax.text(e + pd.Timedelta(days=2), i, name, va="center", fontsize=10, color=col)
    ax.set_yticks([])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlim(t0, pd.Timestamp("2017-09-15"))
    ax.set_title("Validación temporal: cada fold predice 16 días usando solo lo anterior", loc="left", color=INK)
    save(fig, "backtest")


def rmsle_intuicion():
    """RMSLE mide errores relativos: equivocarse ×2 cuesta lo mismo vendas 10 o 10.000."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    y = np.array([10, 100, 1000, 10000])
    for ax, (title, p, fmt) in zip(axes, [("Error absoluto (RMSE)", y * 2, "{:.0f}"), ("Error logarítmico (RMSLE)", y * 2, "{:.2f}")]):
        err = np.abs(p - y) if "RMSE" in title else np.abs(np.log1p(p) - np.log1p(y))
        ax.bar([str(v) for v in y], err, color=[MUTED, MUTED, MUTED, WARN] if "RMSE" in title else ACCENT)
        for i, v in enumerate(err):
            ax.text(i, v, fmt.format(v), ha="center", va="bottom", fontsize=9)
        ax.set_title(title, loc="left")
        ax.set_xlabel("ventas reales (y la predicción es el doble)")
    fig.suptitle("Con RMSLE, las familias pequeñas importan tanto como las grandes", x=0.01, y=1.04, ha="left", color=INK)
    save(fig, "rmsle")


def load():
    if not (DATA / "train.csv").exists():
        print("  (sin data/train.csv: salto las figuras de datos)")
        return None
    return pd.read_csv(DATA / "train.csv", parse_dates=["date"])


def ventas(train):
    d = train.groupby("date")["sales"].sum()
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(d.index, d.values / 1e3, color=MUTED, lw=0.6, label="diaria")
    ax.plot(d.index, d.rolling(28, center=True).mean() / 1e3, color=ACCENT, lw=2, label="media de 4 semanas")
    for date, txt, off in [("2016-04-16", "terremoto", (10, 40)),
                           ("2014-01-01", "1 de enero:\ntiendas cerradas", (-95, 10))]:
        ax.annotate(txt, (pd.Timestamp(date), d.get(pd.Timestamp(date), 0) / 1e3), xytext=off,
                    textcoords="offset points", fontsize=9, color=WARN, arrowprops=dict(arrowstyle="->", color=WARN))
    ax.set_ylabel("miles de unidades")
    ax.set_title("Ventas totales por día (2013–2017): tendencia, picos de diciembre y huecos", loc="left")
    ax.legend(frameon=False)
    save(fig, "ventas")


def semana(train):
    d = train.groupby("date")["sales"].sum().to_frame("s")
    d["dow"], d["dom"] = d.index.dayofweek, d.index.day
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    dow = d.groupby("dow")["s"].mean() / d["s"].mean()
    axes[0].bar(["L", "M", "X", "J", "V", "S", "D"], dow, color=[MUTED] * 5 + [ACCENT] * 2)
    axes[0].axhline(1, color=INK, lw=0.8, ls="--")
    axes[0].set_title("Día de la semana (1 = media)", loc="left")
    dom = d.groupby("dom")["s"].mean() / d["s"].mean()
    axes[1].bar(dom.index, dom, color=[ACCENT if x in (1, 2, 15, 16, 30, 31) else MUTED for x in dom.index])
    axes[1].axhline(1, color=INK, lw=0.8, ls="--")
    axes[1].set_title("Día del mes: se nota la paga (15 y fin de mes)", loc="left")
    save(fig, "semana")


def familias(train):
    f = train.groupby("family")["sales"].sum().sort_values()
    z = train.assign(z=train["sales"] == 0).groupby("family")["z"].mean().reindex(f.index)
    fig, axes = plt.subplots(1, 2, figsize=(10, 7), sharey=True)
    axes[0].barh(f.index, f.values / 1e6, color=ACCENT)
    axes[0].set_title("Ventas totales (millones)", loc="left")
    axes[1].barh(z.index, z.values * 100, color=WARN)
    axes[1].set_title("% de días con 0 ventas", loc="left")
    axes[0].tick_params(axis="y", labelsize=8)
    save(fig, "familias")


def progreso():
    """Evolución del RMSLE de backtest por experimento (eval/results/*.json, sin -quick ni holdout)."""
    res = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "eval" / "results").glob("*.json"))]
    res = [r for r in res if not r["name"].endswith(("-quick", "-holdout"))]
    if not res:
        print("  (sin resultados aún: salto progreso)")
        return
    fig, ax = plt.subplots(figsize=(10, 3.6))
    best = min(r["mean"] for r in res)
    ax.bar([r["name"] for r in res], [r["mean"] for r in res], yerr=[r["std"] for r in res],
           color=[OK if r["mean"] == best else MUTED for r in res], capsize=3)
    ax.set_ylabel("RMSLE backtest (↓ mejor)")
    ax.set_title("Experimentos: media de 4 folds y su dispersión", loc="left")
    ax.tick_params(axis="x", rotation=30)
    save(fig, "progreso")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    o = ap.parse_args(argv)
    simple = {"backtest": backtest, "rmsle": rmsle_intuicion, "progreso": progreso}
    with_data = {"ventas": ventas, "semana": semana, "familias": familias}
    for k, f in simple.items():
        if not o.only or o.only == k:
            f()
    if not o.only or o.only in with_data:
        train = load()
        if train is not None:
            for k, f in with_data.items():
                if not o.only or o.only == k:
                    f(train)


if __name__ == "__main__":
    main()
