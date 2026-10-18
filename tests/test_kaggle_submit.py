"""El botón de subida solo actúa sobre tarjetas de subida y vuelve atrás si Kaggle empeora."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import kaggle_submit as ks  # noqa: E402


def test_vuelve_atras_solo_si_empeora_de_verdad():
    assert ks.should_revert(0.40871, 0.39940)          # v0.6
    assert not ks.should_revert(0.39720, 0.39940)      # v0.7 mejora
    assert not ks.should_revert(0.39960, 0.39940)      # +0.0002: empate
    assert not ks.should_revert(0.40, None)            # primer envío


def test_compara_con_la_mejor_base_activa(tmp_path, monkeypatch):
    monkeypatch.setattr(ks, "RES", tmp_path)
    (tmp_path / "base-v6.json").write_text(json.dumps({"active": False}))
    (tmp_path / "base-v7.json").write_text(json.dumps({}))
    entries = [{"tag": "v0.6", "base": "base-v6", "lb": 0.38},      # retirada: no cuenta aunque su nota sea menor
               {"tag": "v0.7", "base": "base-v7", "lb": 0.39720},
               {"tag": "v0.8", "base": "base-v8", "lb": None}]
    assert ks.previous_lb(entries, "v0.8") == 0.39720


def test_boton_rechaza_tarjetas_que_no_son_de_subida(tmp_path):
    # el servidor carga board.py por ruta: se usa una copia del directorio board/ para no tocar el panel real
    import importlib
    import shutil
    d = tmp_path / "board"
    shutil.copytree(ROOT / "board", d, ignore=shutil.ignore_patterns("runs", "__pycache__", ".lock"))
    sys.path.insert(0, str(d))
    try:
        import server
        importlib.reload(server)
        assert Path(server.__file__).parent == d
        from fastapi.testclient import TestClient
        c = TestClient(server.app)
        tid = c.post("/api/board/task", json={"title": "Otra cosa", "owner": "consultor", "status": "human"}).json()["id"]
        assert c.post(f"/api/kaggle/submit/{tid}").status_code == 409
    finally:
        sys.path.remove(str(d))
