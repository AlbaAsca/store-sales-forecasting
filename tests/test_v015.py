import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("v015", ROOT / "variants" / "V-015" / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_zero_feats():
    m = _load()
    past = np.ones((3, 60))
    past[0, -3:] = 0          # 3 ceros recientes
    past[1, :] = 0            # siempre cero
    f = m._zero_feats(past)
    assert f["since_nz"].tolist() == [3.0, 56.0, 0.0]
    assert np.allclose(f["zfrac14"], [3 / 14, 1, 0])
    assert np.allclose(f["zfrac56"], [3 / 56, 1, 0])
