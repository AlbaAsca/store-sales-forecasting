import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "board"))
import runner  # noqa: E402


def test_pick_skips_contribution_cards():
    t = lambda i, **kw: {"id": i, "owner": "investigador", "status": "doing", "priority": "media", "deps": [], **kw}
    b = {"tasks": [t("T-001", status="next", kind="contrib"), t("T-002", status="backlog")]}
    task, mode = runner.pick(b)
    assert task["id"] == "T-002" and mode == "work"
