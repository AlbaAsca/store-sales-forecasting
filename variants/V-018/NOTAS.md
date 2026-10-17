# V-018: enseñarle la vuelta al cole del año pasado
Se añaden al entrenamiento del modelo directo 4 ejemplos del mismo periodo del año anterior
(orígenes T−16−364+7j, j=−1..2), para que vea un arranque de curso escolar. El recursivo no cambia.
Solo cambia un bloque en `fit_predict` (marcado V-018). Prueba rápida: f1 RMSLE 0.3901 (20 s). Medición completa: tester.
