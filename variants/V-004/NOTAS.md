# V-004 — LightGBM global directo

Sobre base-v2 (media log 14 d + perfil semanal log). En vez de una fórmula por serie, un único LightGBM para las 1782 series
aprende a predecir log1p(ventas) a h=1..16 días. Se entrena apilando 8 cortes (cada 7 días hacia atrás) con rasgos solo del pasado de cada corte:
medias log 3/7/14/28/56 d, perfil del día de la semana objetivo, h, dow, tienda y familia (categóricas). Sin promos/festivos/anual.
Hipótesis: un modelo común capta interacciones (tienda×familia×día) que las medias aisladas no ven. Prueba rápida (fold 1): 0.4040.
Medición completa y veredicto: tester.
