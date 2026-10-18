import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_enlaza_figuras_existentes():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"!\[[^\]]*\]\((docs/img/[^)]+)\)", readme)
    assert {"docs/img/ventas.png", "docs/img/semana.png", "docs/img/familias.png"} <= set(links)
    for link in links:
        p = ROOT / link
        assert p.exists() and p.stat().st_size > 1000, link


def test_readme_enlaza_las_nueve_graficas_de_teorias_y_avisa_mejor_caso():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for n in range(1, 10):
        link = f"docs/img/teorias/base-v{n}.png"
        assert f"]({link})" in readme, link
        assert (ROOT / link).stat().st_size > 1000, link
    assert "mejor caso" in readme


def test_eval_tmp_fuera_de_git():
    lineas = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "eval/tmp/" in [l.strip() for l in lineas]
