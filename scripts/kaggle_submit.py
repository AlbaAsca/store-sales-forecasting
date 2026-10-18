"""Sube un envío a Kaggle cuando Alba pulsa «Subir a Kaggle» en el panel, lee la nota y la apunta.

  python scripts/kaggle_submit.py --card T-074          # lo lanza el servidor del panel (botón)
  python scripts/kaggle_submit.py --card T-074 --dry-run

Solo se ejecuta desde el botón del panel (un clic de Alba por envío). Los agentes del runner no pueden lanzarlo:
tienen denegado `kaggle competitions submit` y el script solo acepta tarjetas «Subir…» en «Te necesita».

Pasos: 1) comprueba el límite diario; 2) sube el CSV con la CLI de Kaggle; 3) espera a que Kaggle puntúe;
4) apunta la nota en eval/kaggle.json, la tarjeta y el gráfico; 5) si la nota es peor que la de la base anterior,
vuelve a esa base, marca la nueva como retirada y abre una tarjeta de diagnóstico para el analista (como con v0.6).
"""
import argparse
import csv
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
COMP = "store-sales-time-series-forecasting"
KAGGLE = os.environ.get("KAGGLE_BIN") or str(ROOT.parent / "KaggleFarm" / ".venv" / "Scripts" / "kaggle.exe")
DAILY_LIMIT = 5        # envíos al día en Kaggle (UTC)
WORSE_TOL = 0.0005     # empeorar menos que esto en Kaggle es empate: no se revierte
sys.path.insert(0, str(ROOT / "board"))


def kaggle(*args):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    r = subprocess.run([KAGGLE, *args], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        raise RuntimeError(f"kaggle {' '.join(args[:2])}: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout


def submissions():
    return list(csv.DictReader(io.StringIO(kaggle("competitions", "submissions", "-c", COMP, "--csv"))))


def score(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def previous_lb(entries, tag):
    """Nota de la base que la nueva sustituye: la mejor nota anterior de una base que siga activa."""
    prev = [e for e in entries if e["tag"] != tag and e.get("lb") is not None and e.get("base", "").startswith("base-v")]
    active = [e for e in prev if (json.loads((RES / f"{e['base']}.json").read_text(encoding="utf-8")).get("active", True)
                                  if (RES / f"{e['base']}.json").exists() else True)]
    return min((e["lb"] for e in active), default=None)


def should_revert(lb, prev):
    return prev is not None and lb > prev + WORSE_TOL


def git(*args):
    subprocess.run(["git", *args], cwd=ROOT, capture_output=True)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wait-min", type=float, default=20)
    o = ap.parse_args(argv)
    import board as bd

    t = bd.task(bd.load(), o.card)
    up = t.get("upload")
    if not up or not t["title"].startswith("Subir") or t["status"] not in ("human", "doing"):
        raise SystemExit(f"{o.card} no es una tarjeta de subida pendiente")
    csv_path = ROOT / up["csv"]
    if not csv_path.exists():
        raise SystemExit(f"No existe {up['csv']}")

    def note(msg, status=None):
        def f(b):
            x = bd.task(b, o.card)
            bd.set_status(b, x, status, "consultor", msg) if status else bd.log(x, "consultor", msg)
        bd.update(f)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    before = submissions()
    used = sum(1 for s in before if s["date"].startswith(today))
    if used >= DAILY_LIMIT:
        note(f"No se sube: ya hay {used} envíos hoy (límite {DAILY_LIMIT} en Kaggle). Vuelve a pulsar mañana.", "human")
        return 3
    if o.dry_run:
        print(f"(dry-run) Subiría {up['csv']} con «{up['message']}». Envíos hoy: {used}/{DAILY_LIMIT}.")
        return 0

    note(f"Subiendo {up['csv']} a Kaggle…", "doing")
    known = {s["ref"] for s in before}
    kaggle("competitions", "submit", COMP, "-f", str(csv_path), "-m", up["message"], "-q")
    lb, deadline = None, time.time() + o.wait_min * 60
    while time.time() < deadline:
        time.sleep(20)
        mine = [s for s in submissions() if s["ref"] not in known and s["fileName"] == csv_path.name]
        if mine and "COMPLETE" in mine[0]["status"]:
            lb = score(mine[0]["publicScore"])
            break
        if mine and "ERROR" in mine[0]["status"]:
            note(f"Kaggle rechazó el fichero: {mine[0]['status']}. Revisa el CSV.", "blocked")
            return 4
    if lb is None:
        note("Subido, pero Kaggle aún no ha devuelto la nota. No vuelvas a pulsar: el consultor la leerá y la apuntará.", "blocked")
        return 5

    kj = ROOT / "eval" / "kaggle.json"
    kd = json.loads(kj.read_text(encoding="utf-8"))
    entry = next((e for e in kd["submissions"] if e["tag"] == up["tag"]), None)
    if entry is None:
        entry = {"tag": up["tag"], "base": up["base"], "lb": None}
        kd["submissions"].append(entry)
    prev = previous_lb(kd["submissions"], up["tag"])
    entry["lb"] = lb
    revert = should_revert(lb, prev)
    msg = f"Kaggle: {lb:.5f}" + (f" (antes {prev:.5f})" if prev is not None else "")

    if revert:
        nb = up["base"]
        k = int(nb.split("-v")[1])
        back = next((f"base-v{i}" for i in range(k - 1, -1, -1)
                     if (RES / f"base-v{i}.json").exists()
                     and json.loads((RES / f"base-v{i}.json").read_text(encoding="utf-8")).get("active", True)), None)
        entry["note"] = f"peor que la base anterior; se vuelve a {back}"
        f = RES / f"{nb}.json"
        d = json.loads(f.read_text(encoding="utf-8"))
        d.update(active=False, note=f"retirada: empeoró en Kaggle ({lb:.5f} frente a {prev:.5f})")
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        if back:
            subprocess.run(["git", "checkout", back, "--", "models/base"], cwd=ROOT, check=True)
        msg += f" → PEOR: se vuelve a {back}."

        def diag(b):
            bd.new_task(b, f"Diagnóstico: por qué {up['tag']} empeoró en Kaggle", "experto", 30, "alta",
                        f"La versión {up['tag']} mejoraba en todas nuestras medidas locales, pero en Kaggle sacó {lb:.5f}, peor que "
                        f"la base anterior ({prev:.5f}). La base ha vuelto atrás automáticamente. Hay que entender qué vio Kaggle que "
                        f"nosotros no, como pasó con v0.6 y las tiendas que cerraron en 2016.\n\nCómo sabremos que está resuelto: "
                        f"una explicación con datos en docs/ANALISIS-ERRORES.md y, si procede, una variante que lo corrija.\n\n"
                        f"## Técnico\n- Comparar dist/{csv_path.name} con el CSV de {back} por tienda, familia y día del test.\n"
                        f"- Buscar anomalías del año anterior o de las semanas previas al corte que la variante {up.get('variant', '')} "
                        f"haya podido trasladar al test.", by="consultor")
        bd.update(diag)
    kj.write_text(json.dumps(kd, ensure_ascii=False, indent=2), encoding="utf-8")
    note(msg, "done")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_figures.py"), "--only", "progreso"], cwd=ROOT)
    git("add", "eval/kaggle.json", "board/board.json", "docs/img/progreso.png", "models/base", str(RES))
    git("commit", "-q", "-m", f"chore(kaggle): record {up['tag']} score {lb:.5f}" + (" and revert base" if revert else "") + f" ({o.card})")
    git("push", "-q", "--follow-tags")
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
