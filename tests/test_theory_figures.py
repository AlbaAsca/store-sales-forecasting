import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from make_theory_figures import pick_series  # noqa: E402


def _serie(store, fam, sales, before, after):
    n = len(sales)
    return pd.DataFrame(dict(store_nbr=[store] * n, family=[fam] * n, sales=sales, before=before, after=after))


def test_elige_mayor_bajada_sin_cerradas_ni_triviales():
    df = pd.concat([
        _serie(1, "A", [100, 100], [50, 50], [90, 90]),      # mejora grande: la elegida
        _serie(2, "B", [100, 100], [60, 60], [70, 70]),      # mejora menor
        _serie(18, "C", [100, 100], [1, 1], [100, 100]),     # tienda cerrada: excluida
        _serie(3, "D", [1, 0], [5, 5], [1, 0]),              # ventas triviales: excluida
    ])
    s, f, b, a = pick_series(df)
    assert (s, f) == (1, "A") and a < b


def test_sin_candidatas():
    assert pick_series(_serie(18, "C", [100], [1], [100])) is None
