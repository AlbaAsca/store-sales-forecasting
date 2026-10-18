"""La promoción automática solo promueve si pasa las mismas comprobaciones que haría el consultor."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "board"))
import promote  # noqa: E402
import runner  # noqa: E402


def res(scores, ctrl_open=0.39):
    return {"folds": [{"id": f"f{i}", "rmsle": v, "by_family": {"A": v}} for i, v in enumerate(scores)],
            "control": [{"id": "c1", "rmsle": 0.75, "rmsle_open": ctrl_open}]}


BASE = res([0.39, 0.38, 0.38, 0.39])
FLAT_ST, FLAT_FA = pd.Series({1: 0.0, 18: 0.01}), pd.Series({"A": 0.02})


def decide(var, holdout_var=0.413, ctrl_var=0.39, st=FLAT_ST, fa=FLAT_FA):
    return promote.decide(BASE, {"V-1": var, "V-1-s7": var}, None, 0.4139, holdout_var, 0.39, ctrl_var, st, fa)


def test_promueve_si_todo_mejora():
    ok, why = decide(res([0.388, 0.379, 0.379, 0.389]))
    assert ok, why


def test_no_promueve_si_empeora_el_examen_final():  # lección de V-019
    ok, why = decide(res([0.388, 0.379, 0.379, 0.389]), holdout_var=0.4227)
    assert not ok and any("examen final empeora" in w for w in why)


def test_no_promueve_si_una_tienda_cambia_de_golpe():  # lección de v0.6 (tiendas 18 y 25)
    ok, why = decide(res([0.388, 0.379, 0.379, 0.389]), st=pd.Series({1: 0.0, 18: -0.178}))
    assert not ok and any("tienda 18" in w for w in why)


def test_no_promueve_si_empeora_dos_practicas():
    ok, _ = decide(res([0.385, 0.381, 0.381, 0.385]))
    assert not ok


def test_control_solo_para_si_empeora_claramente():
    assert decide(res([0.388, 0.379, 0.379, 0.389]), ctrl_var=0.3918)[0]       # +0.0018 (V-027): aviso, no bloquea
    assert not decide(res([0.388, 0.379, 0.379, 0.389]), ctrl_var=0.40)[0]     # +0.01: bloquea


def test_runner_reconoce_las_tarjetas_de_promocion():
    b = {"tasks": [
        {"id": "T-1", "owner": "consultor", "status": "backlog", "title": "Promover V-027 (promos) a base y preparar envío"},
        {"id": "T-2", "owner": "consultor", "status": "done", "title": "Promover V-026 a base"},
        {"id": "T-3", "owner": "desarrollador", "status": "backlog", "title": "Promover V-099 a base"},
        {"id": "T-4", "owner": "consultor", "status": "human", "title": "Subir v0.7 a Kaggle"}]}
    cards = runner.promotion_cards(b)
    assert [t["id"] for t in cards] == ["T-1"]
    assert runner.PROMOTE_RE.match(cards[0]["title"]).group(1) == "V-027"


def test_verificador_mecanico():
    import verify_variant as vv
    runs = {"V-1": res([0.388, 0.379, 0.379, 0.389]), "V-1-s7": res([0.389, 0.379, 0.38, 0.389])}
    assert vv.verdict(BASE, None, runs)["accepted"]
    peor = {"V-1": res([0.385, 0.381, 0.381, 0.385]), "V-1-s7": res([0.385, 0.381, 0.381, 0.385])}
    assert not vv.verdict(BASE, None, peor)["accepted"]
    assert not vv.verdict(BASE, None, {"V-1": runs["V-1"]})["accepted"]          # con una sola semilla no basta


def test_runner_reconoce_variantes_para_verificar():
    assert runner.VARIANT_RE.match("V-031: juntar los tres historiales").group(1) == "V-031"
    assert runner.VARIANT_RE.match("Runner: no bloquear la tarjeta") is None
    assert runner.MAX_TURNS["modelador"] <= 40 and runner.MAX_TURNS["experto"] <= 40
