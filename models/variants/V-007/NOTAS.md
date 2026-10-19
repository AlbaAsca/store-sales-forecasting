# V-007 — objetivo tweedie sobre ventas crudas (sobre base-v3)

Cambia solo la función de pérdida del LightGBM: en vez de L2 sobre log1p(ventas), entrena con `objective="tweedie"` (power 1.3)
sobre las ventas crudas (expm1 del target); los rasgos siguen en log. La predicción sale ya en ventas, sin expm1.
Por qué: tweedie está pensado para series con muchos ceros (M5). Riesgo: la métrica es RMSLE (error en log), y L2 sobre log1p casa exacto con ella.
Prueba rápida (fold 1): 0.4075. Medición completa, semilla alternativa y veredicto: tester.
