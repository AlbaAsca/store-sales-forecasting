"""Estilo común de las figuras del repo: mplcyberpunk (https://github.com/dhaitz/mplcyberpunk).

  import figstyle
  figstyle.apply()                     # antes de crear figuras
  figstyle.glow(ax)                    # brillo neón en las líneas (y relleno suave bajo ellas con under=True)

mplcyberpunk 0.7.6 no se puede importar con matplotlib ≥ 3.11 (usa mpl.style.core.read_style_directory, ya retirado),
así que cargamos su hoja de estilo y su módulo core.py directamente, sin pasar por su __init__.
Si el paquete no está instalado, se usa una copia mínima del estilo para que los scripts no fallen.
"""
import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt

# Paleta neón de mplcyberpunk: cian, rosa, amarillo, verde, violeta, y los grises del fondo
CYAN, PINK, YELLOW, GREEN, VIOLET = "#08F7FE", "#FE53BB", "#F5D300", "#00ff41", "#9467bd"
BG, GRID, INK, MUTED = "#212946", "#2A3459", "#e6e6e6", "#8b93b5"
# Nombres semánticos que usan los scripts
ACCENT, WARN, OK = CYAN, PINK, GREEN

_FALLBACK = {"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "grid.color": GRID,
             "axes.grid": True, "axes.axisbelow": True, "axes.linewidth": 0, "legend.frameon": False,
             "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
             "xtick.major.size": 0, "ytick.major.size": 0, "lines.solid_capstyle": "round",
             "axes.prop_cycle": plt.cycler(color=[CYAN, PINK, YELLOW, GREEN, "r", VIOLET])}


def _pkg():
    spec = importlib.util.find_spec("mplcyberpunk")
    return Path(spec.submodule_search_locations[0]) if spec and spec.submodule_search_locations else None


def _core():
    d = _pkg()
    if not d or not (d / "core.py").exists():
        return None
    spec = importlib.util.spec_from_file_location("_mplcyberpunk_core", d / "core.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def apply():
    d = _pkg()
    sheet = d / "data" / "cyberpunk.mplstyle" if d else None
    plt.style.use(str(sheet) if sheet and sheet.exists() else _FALLBACK)
    plt.rcParams.update({"font.size": 11, "figure.dpi": 110, "savefig.bbox": "tight", "axes.titlecolor": INK})


def glow(ax, under=False, lines=None):
    """Brillo neón de mplcyberpunk en las líneas del eje (o solo en `lines`); under=True añade relleno suave bajo ellas."""
    core = _core()
    if core is None:
        return
    core.make_lines_glow(ax, lines=lines)
    if under:
        core.add_underglow(ax)
