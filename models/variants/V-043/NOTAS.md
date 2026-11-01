# V-043 — predecir cuánto se desvía de su media de 14 días, no el nivel

Antes el modelo aprendía «cuántas unidades (en log)» se venden. Una familia que vende más que nunca queda fuera de lo que los
árboles han visto y se queda corta (p. ej. GROCERY II). Ahora el objetivo es log1p(ventas) menos la media de log1p de los 14 días
previos al corte (los días de tienda cerrada, NaN, no cuentan); al predecir se suma esa media de vuelta antes de expm1.
En el modo recursivo la media se recalcula con lo ya predicho. Series sin datos en 14 días: desfase 0 (objetivo absoluto).
Pendiente del tester: semillas 42 y 7 y mirar GROCERY II en los 4 folds.
