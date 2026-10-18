# V-040 — corregir el sesgo por familia y día de la semana
La base se queda corta siempre en algunas familias (GROCERY II, licores en viernes/sábado). Aquí, antes de predecir, se
vuelve a predecir con el mismo modelo las 2 últimas ventanas de 16 días anteriores al corte (sin verlas), se mide el error
medio en log por (familia, día de la semana) y se suma a la predicción real.
Con prudencia: se encoge hacia 0 (b·n/(n+K), K=200) y se recorta a ±0,25. Env: V040_K, V040_CLIP, V040_WIN (ventanas, 2), V040_ON=0 desactiva.
Coste: ~3× el tiempo de la base (2 ventanas extra); con V040_WIN=1 es ~2×.
