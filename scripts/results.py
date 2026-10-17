"""Resultados del backtest: listar y comparar variante contra base, fold a fold y familia a familia.

  python scripts/results.py list
  python scripts/results.py compare base-v0 V-001 [--max-worse-folds 1]

Veredicto por defecto (CLAUDE.md): ACEPTADA si el RMSLE medio baja y empeora como mucho 1 fold. Exit 0 aceptada, 1 rechazada.
RMSLE: más bajo es mejor.
"""
import argparse
import json
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "eval" / "results"


def load(name):
    f = RESULTS / f"{name}.json"
    if not f.exists():
        sys.exit(f"No existe {f}. Lánzalo antes: python scripts/backtest.py --src ... --name {name}")
    return json.loads(f.read_text(encoding="utf-8"))


def compare(a, b, max_worse_folds=1):
    fa, fb = {f["id"]: f for f in a["folds"]}, {f["id"]: f for f in b["folds"]}
    common = [k for k in fa if k in fb]
    if not common:
        raise ValueError("no hay folds en común: ¿uno es --quick y el otro no?")
    folds = [(k, fa[k]["rmsle"], fb[k]["rmsle"]) for k in common]
    worse = [k for k, x, y in folds if y > x]
    mean_a = sum(x for _, x, _ in folds) / len(folds)
    mean_b = sum(y for _, _, y in folds) / len(folds)
    fam = {}
    for k in common:
        for name, v in fb[k]["by_family"].items():
            fam.setdefault(name, []).append(v - fa[k]["by_family"].get(name, v))
    fam = sorted(((n, sum(d) / len(d)) for n, d in fam.items()), key=lambda x: x[1])
    ok = mean_b < mean_a and len(worse) <= max_worse_folds
    ca, cb = {f["id"]: f["rmsle"] for f in a.get("control", [])}, {f["id"]: f["rmsle"] for f in b.get("control", [])}
    control = [(k, ca[k], cb[k]) for k in ca if k in cb]  # informativo: no entra en media ni en veredicto
    return dict(folds=folds, worse=worse, mean_a=mean_a, mean_b=mean_b, families=fam, accepted=ok, control=control)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list")
    c = sp.add_parser("compare")
    c.add_argument("base")
    c.add_argument("variant")
    c.add_argument("--max-worse-folds", type=int, default=1)
    o = ap.parse_args(argv)

    if o.cmd == "list":
        for f in sorted(RESULTS.glob("*.json")):
            s = json.loads(f.read_text(encoding="utf-8"))
            print(f"{s['name']:24} RMSLE {s['mean']:.4f} ± {s['std']:.4f}  {len(s['folds'])} folds  {s['secs']:>6.0f} s  {s['src']}")
        return 0

    a, b = load(o.base), load(o.variant)
    r = compare(a, b, o.max_worse_folds)
    print(f"{'fold':8} {o.base:>12} {o.variant:>12} {'Δ':>8}")
    for k, x, y in r["folds"]:
        print(f"{k:8} {x:12.4f} {y:12.4f} {y - x:+8.4f} {'peor' if y > x else 'mejor'}")
    print(f"{'media':8} {r['mean_a']:12.4f} {r['mean_b']:12.4f} {r['mean_b'] - r['mean_a']:+8.4f}")
    for k, x, y in r["control"]:
        print(f"{k:8} {x:12.4f} {y:12.4f} {y - x:+8.4f} {'peor' if y > x else 'mejor'}  (control: aparte, no entra en la media)")
    print(f"tiempo: {a['secs']:.0f} s → {b['secs']:.0f} s")
    print("familias que más mejoran: " + ", ".join(f"{n} {d:+.3f}" for n, d in r["families"][:3]))
    print("familias que más empeoran: " + ", ".join(f"{n} {d:+.3f}" for n, d in r["families"][::-1][:3]))
    print(f"VEREDICTO: {'ACEPTADA' if r['accepted'] else 'RECHAZADA'} "
          f"(media {'baja' if r['mean_b'] < r['mean_a'] else 'no baja'}; empeora {len(r['worse'])} fold(s), máx. {o.max_worse_folds})")
    return 0 if r["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
