"""Servidor del panel: http://localhost:8021/  (FastAPI, sin dependencias del proyecto).

Uso: python board/server.py [--port 8021]
Puede convivir con el servidor de tu proyecto (otro puerto).
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response

HERE = Path(__file__).parent
BOARD = HERE / "board.json"
app = FastAPI(title="Panel de agentes")


def _bd():
    spec = importlib.util.spec_from_file_location("board", HERE / "board.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@app.get("/")
def panel():
    return FileResponse(HERE / "panel.html", headers={"Cache-Control": "no-store"})


AGENTS_DIR = HERE.parent / ".claude" / "agents"


def agent_config(aid):
    """model/effort del frontmatter de .claude/agents/<id>.md (se lee en cada petición: siempre al día)."""
    f = AGENTS_DIR / f"{aid}.md"
    if not f.is_file():
        return {}
    m = re.match(r"---\s*\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S)
    return dict(re.findall(r"^(model|effort):\s*(\S+)", m.group(1), re.M)) if m else {}


@app.get("/api/board")
def get_board():
    b = json.loads(BOARD.read_text(encoding="utf-8"))
    for a in b.get("agents", []):
        a.update(agent_config(a["id"]))
    r = b.setdefault("runner", {})
    r["alive"] = pid_alive(r.get("pid"))
    live = HERE / "runs" / r["live"] if r.get("live") else None
    r["last_activity"] = (datetime.fromtimestamp(live.stat().st_mtime).astimezone().isoformat(timespec="seconds")
                          if live and live.is_file() else None)  # última línea que escribió el agente
    return Response(json.dumps(b, ensure_ascii=False), media_type="application/json", headers={"Cache-Control": "no-store"})


EDITABLE = {"title", "owner", "priority", "estimate_min", "desc", "deps", "manual"}


@app.patch("/api/board/task/{tid}")
async def patch_task(tid: str, request: Request):
    """Edita una tarea. El estado pasa por set_status para que los tiempos reales se registren solos."""
    body, bd = await request.json(), _bd()

    def f(b):
        t = bd.task(b, tid)
        changed = [k for k in EDITABLE if k in body and body[k] != t.get(k)]
        for k in changed:
            t[k] = body[k]
        if "manual" in changed:
            t["auto"] = not body["manual"]
        if changed:
            bd.log(t, "tú", "editada: " + ", ".join(changed))
        if body.get("status") and body["status"] != t["status"]:
            bd.set_status(b, t, body["status"], "tú")
        if body.get("note"):
            bd.log(t, "tú", body["note"])
    try:
        bd.update(f)
    except (StopIteration, AssertionError) as e:
        raise HTTPException(400, str(e) or "tarea no encontrada")
    return {"ok": True}


@app.delete("/api/board/task/{tid}")
def delete_task(tid: str):
    bd = _bd()

    def f(b):
        n = len(b["tasks"])
        b["tasks"] = [t for t in b["tasks"] if t["id"] != tid]
        if len(b["tasks"]) == n:
            raise HTTPException(404, "tarea no encontrada")
    bd.update(f)
    return {"ok": True}


@app.post("/api/board/task")
async def create_task(request: Request):
    body, bd = await request.json(), _bd()
    try:
        t = bd.update(lambda b: bd.new_task(b, body["title"], body["owner"], body.get("estimate_min") or 10,
                                            body.get("priority", "media"), body.get("desc", ""),
                                            body.get("status", "backlog"), body.get("manual") or None, "tú"))
    except (KeyError, AssertionError) as e:
        raise HTTPException(400, str(e))
    return {"id": t["id"]}


@app.post("/api/board/runner")
async def runner_toggle(request: Request):
    enabled, bd = bool((await request.json()).get("enabled")), _bd()

    def f(b):
        b.setdefault("runner", {})["enabled"] = enabled
    bd.update(f)
    return {"enabled": enabled}


# ---- Control del runner desde el panel (Windows) ----
ROOT = HERE.parent
TASK_NAME = "store-sales runner"  # tarea del Programador de tareas (run-agents-scheduled.bat)
_sched_cache = {"t": 0, "v": None}


def pid_alive(pid):
    return _bd().pid_alive(pid)


def claude_bin():
    found = shutil.which("claude")
    if found:
        return found
    hits = sorted(Path(os.environ.get("APPDATA", "")).glob("Claude/claude-code/*/*/claude.exe"), key=lambda p: p.stat().st_mtime)
    return str(hits[-1]) if hits else "claude"


@app.get("/api/runner/schedule")
def runner_schedule():
    """Próxima y última ejecución automática (Programador de tareas). Cacheado 60 s."""
    if time.time() - _sched_cache["t"] < 60 and _sched_cache["v"]:
        return _sched_cache["v"]
    v = {"task": TASK_NAME, "exists": False}
    if os.name == "nt":
        ps = (f"$t=Get-ScheduledTask -TaskName '{TASK_NAME}' -ErrorAction SilentlyContinue; if($t){{$i=$t|Get-ScheduledTaskInfo;"
              "@{state=[string]$t.State;next=$i.NextRunTime.ToString('s');last=$i.LastRunTime.ToString('s');"
              "result=$i.LastTaskResult}|ConvertTo-Json -Compress}")
        try:
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                                 timeout=20, creationflags=0x08000000).stdout.strip()
            if out:
                v.update(json.loads(out), exists=True)
        except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as e:
            v["error"] = str(e)
    _sched_cache.update(t=time.time(), v=v)
    return v


def _short(x, n=220):
    x = " ".join(str(x).split())
    return x if len(x) <= n else x[:n] + "…"


def live_events(lines):
    """Resume los eventos stream-json de la CLI en líneas legibles: qué piensa, qué herramienta usa y qué le devuelve."""
    out = []
    for line in lines:
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        typ = e.get("type")
        if typ == "system" and e.get("subtype") == "init":
            out.append({"kind": "inicio", "text": f"modelo {e.get('model', '?')}"})
        elif typ in ("assistant", "user"):
            for c in (e.get("message") or {}).get("content") or []:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "text" and c.get("text", "").strip():
                    out.append({"kind": "texto", "text": _short(c["text"], 600)})
                elif c.get("type") == "thinking" and c.get("thinking", "").strip():
                    out.append({"kind": "piensa", "text": _short(c["thinking"], 600)})
                elif c.get("type") == "tool_use":
                    i = c.get("input") or {}
                    arg = i.get("command") or i.get("file_path") or i.get("pattern") or i.get("query") or i.get("url") or i.get("description") or ""
                    out.append({"kind": "herramienta", "text": f"{c.get('name')}: {_short(arg, 300)}"})
                elif c.get("type") == "tool_result":
                    body = c.get("content")
                    if isinstance(body, list):
                        body = " ".join(x.get("text", "") for x in body if isinstance(x, dict))
                    out.append({"kind": "error" if c.get("is_error") else "resultado", "text": _short(body or "(vacío)")})
        elif typ == "result":
            out.append({"kind": "fin", "text": _short(e.get("result") or e.get("subtype") or "", 400)})
    return out


@app.get("/api/runner/live")
def runner_live(n: int = 60):
    """Lo que está haciendo el agente ahora (o hizo en la última ejecución), sin gastar tokens: lee el log en vivo."""
    runs = HERE / "runs"
    name = json.loads(BOARD.read_text(encoding="utf-8")).get("runner", {}).get("live")
    f = runs / name if name and (runs / name).is_file() else None
    if not f:
        files = sorted(runs.glob("live-*.jsonl"), key=lambda x: x.stat().st_mtime) if runs.is_dir() else []
        f = files[-1] if files else None
    if not f:
        return {"file": None, "events": []}
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]
    return {"file": f.name, "events": live_events(lines)[-n:]}


@app.post("/api/runner/start")
def runner_start():
    """Arranca el runner en segundo plano: trabaja tarea tras tarea y se para cuando no quedan (--until-idle)."""
    b = json.loads(BOARD.read_text(encoding="utf-8"))
    if pid_alive(b.get("runner", {}).get("pid")):
        raise HTTPException(409, "El runner ya está en marcha")
    bd = _bd()
    bd.update(lambda x: x.setdefault("runner", {}).update(enabled=True))
    env = dict(os.environ, PYTHONUTF8="1", CLAUDE_BIN=claude_bin())
    venv = ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    env["PATH"] = f"{venv}{os.pathsep}{env.get('PATH', '')}"
    (HERE / "runs").mkdir(exist_ok=True)
    log = open(HERE / "runs" / "panel.log", "a", encoding="utf-8")
    flags = 0x00000008 | 0x00000200 | 0x08000000 if os.name == "nt" else 0  # DETACHED | NEW_GROUP | NO_WINDOW
    args = dict(cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    cmd = [sys.executable, str(HERE / "runner.py"), "--until-idle", "--contribute"]
    try:  # fuera del "job" del proceso padre: si no, Windows lo mata cuando el padre termina
        p = subprocess.Popen(cmd, creationflags=flags | (0x01000000 if os.name == "nt" else 0), **args)
    except OSError:
        p = subprocess.Popen(cmd, creationflags=flags, **args)
    return {"ok": True, "pid": p.pid}


@app.post("/api/runner/stop")
def runner_stop():
    """Para el runner y al agente que esté trabajando (mata el árbol de procesos). La tarea vuelve a Próximo."""
    bd = _bd()
    pid = bd.load().get("runner", {}).get("pid")
    if pid_alive(pid):
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, creationflags=0x08000000)
        else:
            os.kill(pid, 15)

    def f(b):
        for t in b["tasks"]:
            if t["status"] == "doing" and t.get("kind") == "contrib":
                bd.set_status(b, t, "done", "tú", "ronda parada desde el panel")
            elif t["status"] == "doing" and t["owner"] != "consultor":
                bd.set_status(b, t, "next", "tú", "parada desde el panel; se reintentará")
        for a in b["agents"]:
            if a["id"] != "consultor":
                a.update(status="idle", current=None)
        b.setdefault("runner", {}).update(state="stopped", current=None, message="Parado desde el panel", heartbeat=bd.now())
    bd.update(f)
    return {"ok": True, "killed": bool(pid)}


if __name__ == "__main__":
    import uvicorn
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8021)
    uvicorn.run(app, host="127.0.0.1", port=ap.parse_args().port)
