# V-011 — promos acotadas al rango de entrenamiento
Cambio único: `promo_day` y `promo_ratio` se recortan, por familia, al percentil 99 que se ve en los cortes de entrenamiento (en entrenamiento y en predicción).
Por qué: el 16-ago del test trae un pico de promos nunca visto (LAWN 842 vs máx. 212) y el modelo triplicaba la venta de SCHOOL/LAWN/LINGERIE.
Criterio (fijado antes): CV ≤ base-v3 + 0.001, ningún fold > +0.003, y predicción 16-ago ≤ ×1.5 la del 17-ago en esas familias.
Humo: `--quick` fold 1 RMSLE 0.3953. Falta medición completa del tester.
