"""Imprime las celdas de código y markdown de un .ipynb (sin salidas). Uso: python -I scripts/analysis/ipynb_code.py <ruta> [max_chars]"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
nb = json.load(open(sys.argv[1], encoding="utf-8"))
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
out = []
for c in nb["cells"]:
    s = "".join(c["source"])
    if c["cell_type"] == "markdown":
        s = "# MD: " + s[:300]
    out.append(s)
t = "\n----\n".join(out)
print(t[:lim])
