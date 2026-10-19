# V-027: promociones de los días de alrededor
Antes el modelo solo veía la promoción del día a predecir. Ahora también ve la del día anterior, la del siguiente
y el total de promociones de los 16 días a predecir (todo conocido de antemano, sin fuga).
Cambio solo en `_features` (modo directo) y `_step_feats` (recursivo): `promo_fut16`, `promo_prev_day`, `promo_next_day`
(NaN el último día del bloque). En el modo recursivo `promo_fut16` suma los 16 días desde el día objetivo.
