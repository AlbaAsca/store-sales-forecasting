# V-040 — corregir el sesgo por familia y día de la semana
La base se queda corta siempre en algunas familias (GROCERY II, licores en viernes/sábado). Aquí, antes de predecir, se
vuelve a predecir con el mismo modelo la última ventana de 16 días anterior al corte (sin verla), se mide el error
medio en log por (familia, día de la semana) y se suma a la predicción real.
Con prudencia: se encoge hacia 0 (b·n/(n+K), K=200) y se recorta a ±0,25. Env: V040_K, V040_CLIP, V040_WIN (ventanas, por defecto 1), V040_ON=0 desactiva.
Coste: ~2× la base (125 s/fold → ~250 s); con V040_WIN=2 sería ~3× (>15 min por medición completa).
