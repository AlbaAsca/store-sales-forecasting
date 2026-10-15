"""Entrena con TODO train y predice test.csv → dist/submission-<nombre>.csv (formato de Kaggle: id,sales).

  python scripts/make_submission.py --src models/base --name base-v0

Subirlo a Kaggle lo hace Alba a mano (los agentes nunca envían). Antes: tag vX.Y y resultado de holdout (CLAUDE.md).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from backtest import DATA, ROOT, load_data, load_model  # noqa: E402


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--seed", type=int, default=42)
    o = ap.parse_args(argv)
    train, ctx = load_data()
    test = pd.read_csv(DATA / "test.csv", parse_dates=["date"], dtype={"family": "category"})
    p = np.clip(np.asarray(load_model(o.src).fit_predict(train, test, {**ctx, "seed": o.seed}), float), 0, None)
    assert len(p) == len(test) and np.isfinite(p).all()
    out = ROOT / "dist" / f"submission-{o.name}.csv"
    out.parent.mkdir(exist_ok=True)
    pd.DataFrame({"id": test["id"], "sales": p}).to_csv(out, index=False)
    print(f"OK -> {out.relative_to(ROOT).as_posix()} ({len(p)} filas). Súbelo a mano en Kaggle con el tag en el mensaje.")


if __name__ == "__main__":
    main()
