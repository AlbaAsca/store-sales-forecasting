"""Estilo común de las figuras del repo: paleta Tokyo Night (https://github.com/folke/tokyonight.nvim).

  import figstyle
  figstyle.apply()                     # antes de crear figuras
  figstyle.glow(ax)                    # halo suave bajo las líneas (y relleno tenue bajo ellas con under=True)

Sustituye al estilo mplcyberpunk anterior con la misma API, así que los scripts no cambian.
"""
import matplotlib.pyplot as plt

# Paleta Tokyo Night. Los nombres antiguos (CYAN, PINK...) se mantienen para no tocar los scripts.
CYAN, PINK, YELLOW, GREEN, VIOLET = "#7DCFFF", "#F7768E", "#E0AF68", "#9ECE6A", "#BB9AF7"
BLUE, ORANGE = "#7AA2F7", "#FF9E64"
BG, GRID, INK, MUTED = "#1A1B26", "#292E42", "#C0CAF5", "#9AA5CE"
# Nombres semánticos que usan los scripts
ACCENT, WARN, OK = CYAN, PINK, GREEN

_STYLE = {"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "grid.color": GRID,
          "axes.grid": True, "axes.axisbelow": True, "axes.linewidth": 0, "legend.frameon": False,
          "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
          "legend.labelcolor": MUTED, "axes.titlecolor": INK,
          "xtick.major.size": 0, "ytick.major.size": 0, "lines.solid_capstyle": "round",
          "axes.prop_cycle": plt.cycler(color=[CYAN, PINK, YELLOW, GREEN, BLUE, VIOLET, ORANGE])}


def apply():
    plt.style.use(_STYLE)
    plt.rcParams.update({"font.size": 11, "figure.dpi": 110, "savefig.bbox": "tight"})


def glow(ax, under=False, lines=None):
    """Halo suave bajo las líneas del eje (o solo `lines`); under=True añade un relleno tenue hasta el borde inferior."""
    for ln in list(lines if lines is not None else ax.get_lines()):
        x, y = ln.get_data()
        if len(x) < 2:
            continue
        color = ln.get_color()
        halo = ax.plot(x, y, color=color, linewidth=ln.get_linewidth() * 3, alpha=0.12,
                       solid_capstyle="round", zorder=ln.get_zorder() - 0.1)[0]
        halo.set_label("_nolegend_")  # el halo no va a la leyenda
        if under:
            ax.fill_between(x, y, ax.get_ylim()[0], color=color, alpha=0.06, zorder=ln.get_zorder() - 0.2)
