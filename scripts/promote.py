"""Promoción automática de una variante aceptada a nueva base + envío listo para Kaggle (sin agente: 0 tokens).

  python scripts/promote.py V-027            # comprueba, y si pasa: promueve, genera CSV, tags y tarjeta de subida
  python scripts/promote.py V-027 --dry-run  # solo comprueba y explica

Lo lanza el runner cuando el tester crea la tarjeta «Promover V-xxx…» para el consultor (o el consultor a mano).
Hace las mismas comprobaciones que el consultor, aprendidas de los envíos anteriores:
  1. Prácticas: la variante baja la media de la base con todas las semillas medidas y empeora como mucho 1 fold.
  2. Examen final (holdout): no empeora (lo mide aquí; v0.6 y V-019 enseñaron que la media de folds no basta).
  3. Control sin tiendas cerradas: no empeora más de CONTROL_TOL (es solo un aviso suave).
  4. Test de Kaggle: ninguna tienda ni familia cambia de golpe frente a la base (v0.6 hundió las tiendas 18 y 25 un 16 %).
Si algo falla, no promueve: explica qué y por qué, y la tarjeta queda para que el consultor decida.
Nunca envía nada a Kaggle: la subida es una tarjeta «Te necesita» para Alba.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "board"))

HOLDOUT_TOL = 0.0005   # el examen final puede empatar, no empeorar
CONTROL_TOL = 0.003    # el control sin cerradas es un aviso: solo para si empeora claramente
STORE_SHIFT = 0.05     # cambio medio en log por tienda frente a la base en el test (v0.6: −0.178)
FAMILY_SHIFT = 0.10    # ídem por familia


def load(name):
    f = RES / f"{name}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def current_base():
    """Número y resultados de la base vigente (la del tag base-vN más alto cuyo resultado existe)."""
    tags = subprocess.run(["git", "tag", "--list", "base-v*"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    nums = sorted(int(m.group(1)) for t in tags if (m := re.fullmatch(r"base-v(\d+)", t)))
    n = nums[-1] if nums else 0
    # una base retirada (como base-v6 tras empeorar en Kaggle) no es la vigente: la vigente es la que está en models/base
    for k in reversed(nums):
        r = load(f"base-v{k}")
        if r and r.get("active", True):
            return k, n, r
    raise SystemExit("No encuentro resultados de la base vigente en eval/results/base-vN.json")


def open_ctrl(r):
    return next((f.get("rmsle_open") for f in (r or {}).get("control", []) if "rmsle_open" in f), None)


def store_family_shift(base_csv, var_csv, test):
    a, b = pd.read_csv(base_csv), pd.read_csv(var_csv)
    d = np.log1p(b["sales"].to_numpy()) - np.log1p(a["sales"].to_numpy())
    st = pd.Series(d).groupby(test["store_nbr"].to_numpy()).mean()
    fa = pd.Series(d).groupby(test["family"].to_numpy()).mean()
    return st, fa


def decide(base, var_runs, base_s7, holdout_base, holdout_var, ctrl_base, ctrl_var, store_shift, family_shift):
    """Devuelve (ok, motivos). Función pura para poder probarla."""
    from results import compare
    reasons, ok = [], True
    for name, run in var_runs.items():
        ref = base_s7 if name.endswith("-s7") and base_s7 else base
        c = compare(ref, run)
        if not c["accepted"]:
            ok = False
            reasons.append(f"prácticas ({name}): media {c['mean_b']:.4f} frente a {c['mean_a']:.4f}, empeora {len(c['worse'])} folds")
        else:
            reasons.append(f"prácticas ({name}): {c['mean_a']:.4f} → {c['mean_b']:.4f}, empeora {len(c['worse'])} fold(s)")
    if holdout_var > holdout_base + HOLDOUT_TOL:
        ok = False
        reasons.append(f"examen final empeora: {holdout_base:.4f} → {holdout_var:.4f}")
    else:
        reasons.append(f"examen final: {holdout_base:.4f} → {holdout_var:.4f}")
    if ctrl_base is not None and ctrl_var is not None:
        if ctrl_var > ctrl_base + CONTROL_TOL:
            ok = False
            reasons.append(f"control sin cerradas empeora claramente: {ctrl_base:.4f} → {ctrl_var:.4f}")
        else:
            reasons.append(f"control sin cerradas: {ctrl_base:.4f} → {ctrl_var:.4f}")
    bad_st = store_shift[store_shift.abs() > STORE_SHIFT]
    bad_fa = family_shift[family_shift.abs() > FAMILY_SHIFT]
    if len(bad_st) or len(bad_fa):
        ok = False
        reasons.append("en el test cambian de golpe frente a la base: "
                       + ", ".join([f"tienda {k} {v:+.3f}" for k, v in bad_st.items()]
                                   + [f"{k} {v:+.3f}" for k, v in bad_fa.items()]))
    else:
        reasons.append(f"test: ninguna tienda cambia más de {STORE_SHIFT} ni familia más de {FAMILY_SHIFT} en log "
                       f"(máx. tienda {store_shift.abs().max():.3f}, familia {family_shift.abs().max():.3f})")
    return ok, reasons


def run_py(*args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", help="V-xxx (carpeta en variants/)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--card", help="tarjeta del panel que se cierra con el resultado (T-xxx)")
    o = ap.parse_args(argv)
    v = o.variant
    src = ROOT / "variants" / v
    if not (src / "model.py").exists():
        raise SystemExit(f"No existe variants/{v}/model.py")
    k, last, base = current_base()
    base_name = f"base-v{k}"
    var_runs = {n: r for n in (v, f"{v}-s7") if (r := load(n))}
    if not var_runs:
        raise SystemExit(f"Faltan los resultados del tester: eval/results/{v}.json")
    base_s7 = load(f"{base_name}-s7") or load(f"{base.get('from', '')}-s7")

    print(f"Comprobando {v} frente a {base_name}…")
    if not load(f"{v}-holdout"):
        run_py("scripts/backtest.py", "--src", f"variants/{v}", "--name", f"{v}-holdout", "--holdout")
    if not (ROOT / "dist" / f"submission-{v}.csv").exists():
        run_py("scripts/make_submission.py", "--src", f"variants/{v}", "--name", v)
    base_csv = ROOT / "dist" / f"submission-{base_name}.csv"
    if not base_csv.exists():
        run_py("scripts/make_submission.py", "--src", "models/base", "--name", base_name)
    test = pd.read_csv(ROOT / "data" / "test.csv")
    st, fa = store_family_shift(base_csv, ROOT / "dist" / f"submission-{v}.csv", test)
    ok, reasons = decide(base, var_runs, base_s7, load(f"{base_name}-holdout")["mean"], load(f"{v}-holdout")["mean"],
                         open_ctrl(base), open_ctrl(var_runs[v]), st, fa)
    for r in reasons:
        print(("  ✓ " if ok else "  · ") + r)
    new = last + 1
    summary = f"{v} → base-v{new}: " + "; ".join(reasons)
    if not ok:
        print(f"NO SE PROMUEVE {v}. La base sigue siendo {base_name}.")
        _close_card(o.card, f"NO se promueve {v} (comprobación automática): " + "; ".join(reasons), promoted=False)
        return 2
    if o.dry_run:
        print(f"(dry-run) Se promovería {v} a base-v{new}.")
        return 0

    nb = f"base-v{new}"
    shutil.rmtree(ROOT / "models" / "base")
    shutil.copytree(src, ROOT / "models" / "base", ignore=shutil.ignore_patterns("__pycache__"))
    for s, dname in ((v, nb), (f"{v}-holdout", f"{nb}-holdout"), (f"{v}-s7", f"{nb}-s7")):
        r = load(s)
        if r:
            r.update(name=dname, src="models/base", **({"from": v} if dname == nb else {}))
            (RES / f"{dname}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(ROOT / "dist" / f"submission-{v}.csv", ROOT / "dist" / f"submission-{nb}.csv")
    tag = f"v0.{new}"
    kj = ROOT / "eval" / "kaggle.json"
    kd = json.loads(kj.read_text(encoding="utf-8"))
    kd["submissions"].append({"tag": tag, "base": nb, "cv": round(var_runs[v]["mean"], 4),
                              "holdout": round(load(f"{v}-holdout")["mean"], 4), "lb": None, "date": pd.Timestamp.now().strftime("%Y-%m-%d")})
    kj.write_text(json.dumps(kd, ensure_ascii=False, indent=2), encoding="utf-8")
    msg = (f"{tag} · {nb} ({v}) · backtest {var_runs[v]['mean']:.4f} · holdout {load(f'{v}-holdout')['mean']:.4f}")
    subprocess.run(["git", "add", "models/base", "eval/kaggle.json", str(RES / f"{nb}.json"), str(RES / f"{nb}-holdout.json")]
                   + ([str(RES / f"{nb}-s7.json")] if load(f"{nb}-s7") else []) + [str(RES / f"{v}-holdout.json")],
                   cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-q", "-m", f"feat(model): promote {v} to {nb} (automatic promotion)"], cwd=ROOT, check=True)
    subprocess.run(["git", "tag", "-a", nb, "-m", f"{nb} = {v}"], cwd=ROOT, check=True)
    subprocess.run(["git", "tag", "-a", tag, "-m", msg], cwd=ROOT, check=True)
    print(f"PROMOVIDA: {nb} = {v}. CSV: dist/submission-{nb}.csv · tags {nb} y {tag}.")
    _close_card(o.card, f"Promovida automáticamente: {summary}", promoted=True, upload=(nb, tag, msg, reasons))
    return 0


def _close_card(card, msg, promoted, upload=None):
    import board as bd

    def f(b):
        if card:
            t = bd.task(b, card)
            bd.set_status(b, t, "done" if promoted else "blocked", "consultor", msg[:900])
        if upload:
            nb, tag, m, reasons = upload
            bd.new_task(b, f"Subir {tag} ({nb}) a Kaggle y apuntar la puntuación", "consultor", 3, "alta",
                        f"La comprobación automática ha preparado una nueva base: mejora en las prácticas y no empeora el examen "
                        f"final, el control ni ninguna tienda del test. Toca subirla y ver qué dice Kaggle.\n\n## Técnico\n"
                        + "\n".join(f"- {r}" for r in reasons) + f"\n- CSV: dist/submission-{nb}.csv",
                        status="human", manual=f"Kaggle > Store Sales > Submit Prediction > subir dist/submission-{nb}.csv con el "
                                               f"mensaje: {m}. Pasar la puntuación al consultor.", by="consultor")
    bd.update(f)


if __name__ == "__main__":
    sys.exit(main())
