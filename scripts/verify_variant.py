"""Verificación mecánica de una variante (sin agente: 0 tokens). La lanza el runner antes de llamar al evaluador.

  python scripts/verify_variant.py V-031            # mide lo que falte (semillas 42 y 7) y da el veredicto
  python scripts/verify_variant.py V-031 --env V032_W=0.2

Hace lo que antes hacía el evaluador a mano: backtest con las dos semillas (reutiliza resultados ya medidos), comparación
fold a fold con la base vigente y su misma semilla, control sin tiendas cerradas, tiempo. Escribe eval/results/<V>-verdict.json
y una tabla en texto que el runner le pasa al evaluador, que solo tiene que revisar el código y escribir las conclusiones.
Exit 0 = ACEPTADA según el criterio por defecto de CLAUDE.md; 1 = RECHAZADA; 2 = no se pudo medir.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
sys.path.insert(0, str(ROOT / "scripts"))
from promote import current_base, load, open_ctrl  # noqa: E402
from results import compare  # noqa: E402

SEEDS = (("", 42), ("-s7", 7))


def measure(v, suffix, seed, env):
    name = f"{v}{suffix}"
    if load(name):
        return load(name)
    cmd = [sys.executable, str(ROOT / "scripts" / "backtest.py"), "--src", f"variants/{v}", "--name", name, "--seed", str(seed)]
    for e in env:
        cmd += ["--env", e]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"backtest {name} falló:\n{r.stderr[-1500:]}")
    return load(name)


def verdict(base, base_s7, runs):
    """Función pura: dict con filas por semilla, veredicto y motivos."""
    rows, ok, why = [], True, []
    for name, run in runs.items():
        ref = base_s7 if name.endswith("-s7") and base_s7 else base
        c = compare(ref, run)
        rows.append({"run": name, "base": round(c["mean_a"], 4), "variant": round(c["mean_b"], 4),
                     "delta": round(c["mean_b"] - c["mean_a"], 4), "worse_folds": c["worse"],
                     "folds": [[k, round(a, 4), round(b, 4)] for k, a, b in c["folds"]],
                     "families_best": [[n, round(d, 3)] for n, d in c["families"][:3]],
                     "families_worst": [[n, round(d, 3)] for n, d in c["families"][::-1][:3]]})
        if not c["accepted"]:
            ok = False
            why.append(f"{name}: media {c['mean_a']:.4f} → {c['mean_b']:.4f}, empeora {len(c['worse'])} fold(s)")
    return {"accepted": ok and len(runs) >= 2, "rows": rows,
            "why": why or (["solo hay una semilla"] if len(runs) < 2 else [])}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("variant")
    ap.add_argument("--env", action="append", default=[])
    o = ap.parse_args(argv)
    v = o.variant
    if not (ROOT / "variants" / v / "model.py").exists():
        print(f"No existe variants/{v}/model.py")
        return 2
    k, _, base = current_base()
    bn = f"base-v{k}"
    base_s7 = load(f"{bn}-s7") or load(f"{base.get('from', '')}-s7")
    try:
        runs = {f"{v}{s}": measure(v, s, seed, o.env) for s, seed in SEEDS}
    except RuntimeError as e:
        print(e)
        return 2
    out = verdict(base, base_s7, runs)
    out.update(variant=v, base=bn, control_open={"base": open_ctrl(base), "variant": open_ctrl(runs[v])},
               secs={"base": base.get("secs"), "variant": runs[v].get("secs")})
    (RES / f"{v}-verdict.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"VERIFICACIÓN AUTOMÁTICA de {v} frente a {bn} (criterio por defecto: media menor con 2 semillas, ≤ 1 fold peor)")
    for r in out["rows"]:
        print(f"- {r['run']}: {r['base']:.4f} → {r['variant']:.4f} ({r['delta']:+.4f}); folds peores: {r['worse_folds'] or 'ninguno'}")
        print("    por fold: " + " · ".join(f"{f} {a:.4f}→{b:.4f}" for f, a, b in r["folds"]))
        print("    familias que más mejoran: " + ", ".join(f"{n} {d:+.3f}" for n, d in r["families_best"])
              + " · que más empeoran: " + ", ".join(f"{n} {d:+.3f}" for n, d in r["families_worst"]))
    co = out["control_open"]
    if co["base"] is not None and co["variant"] is not None:
        print(f"- control sin tiendas cerradas: {co['base']:.4f} → {co['variant']:.4f}")
    print(f"- tiempo de un backtest: {out['secs']['base']} s → {out['secs']['variant']} s")
    print("VEREDICTO: " + ("ACEPTADA" if out["accepted"] else "RECHAZADA (" + "; ".join(out["why"]) + ")"))
    return 0 if out["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
