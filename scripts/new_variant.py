"""Crea variants/<V-xxx>/ como copia exacta de models/base/ (la base vigente).

Uso: python scripts/new_variant.py V-012
Los agentes del runner pueden ejecutarlo siempre (python está permitido); así no dependen de cp/Copy-Item.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or not re.fullmatch(r"V-\d{3}[A-Za-z0-9-]*", args[0]):
        sys.exit("Uso: python scripts/new_variant.py V-xxx   (p. ej. V-012 o V-012-tweedie)")
    dst = ROOT / "variants" / args[0]
    if dst.exists():
        sys.exit(f"Ya existe {dst.relative_to(ROOT)}: edítala en vez de crearla")
    shutil.copytree(ROOT / "models" / "base", dst, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"OK -> {dst.relative_to(ROOT).as_posix()} (copia de models/base/). Cambia solo lo de tu variante.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
