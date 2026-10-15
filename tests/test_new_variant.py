import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import new_variant  # noqa: E402


def test_copia_la_base(tmp_path, monkeypatch):
    (tmp_path / "models" / "base").mkdir(parents=True)
    (tmp_path / "models" / "base" / "model.py").write_text("x = 1\n")
    monkeypatch.setattr(new_variant, "ROOT", tmp_path)
    assert new_variant.main(["V-001"]) == 0
    assert (tmp_path / "variants" / "V-001" / "model.py").read_text() == "x = 1\n"
