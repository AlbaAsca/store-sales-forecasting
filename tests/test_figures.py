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
