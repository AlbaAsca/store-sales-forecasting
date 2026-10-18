"""Líneas de un .ipynb (código+markdown) que casan con una regex. Uso: python -I scripts/analysis/ipynb_grep.py <ruta> <regex> [max_lineas]"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
nb = json.load(open(sys.argv[1], encoding="utf-8"))
rx = re.compile(sys.argv[2], re.I)
lim = int(sys.argv[3]) if len(sys.argv) > 3 else 60
n = 0
for i, c in enumerate(nb["cells"]):
    for ln in "".join(c["source"]).splitlines():
        if rx.search(ln):
            print(f"[{i}{c['cell_type'][0]}] {ln[:260]}")
            n += 1
            if n >= lim:
                sys.exit()
