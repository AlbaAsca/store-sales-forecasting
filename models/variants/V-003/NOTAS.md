# V-003: ajuste por promociones en log (sobre V-002)

Con más promos de lo habitual en los últimos 14 días la base predecía de menos, y con menos, de más (hallazgo 8).
Cambio: a la predicción en log se suma beta_familia × (log1p(promos del día) − media de log1p(promos) 14 d).
beta = pendiente por familia (180 d previos al corte, valores centrados por tienda×familia×día de semana), limitada a [0, 0.5].
Criterio fijado: RMSLE medio < base vigente, empeora ≤1 de 4 folds; si gana < 0.002, rechazar por complejidad.
