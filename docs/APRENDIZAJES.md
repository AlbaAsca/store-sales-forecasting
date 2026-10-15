# Aprendizajes

Bitácora de experimentos: 2-3 líneas por experimento cerrado (**qué se probó · qué pasó · por qué**), del más reciente al más antiguo.
Los conceptos nuevos se explican en el [glosario](#glosario) la primera vez que aparecen.

## Experimentos

### v0.2 · segundo envío: ¿a quién creer, a los folds o al holdout? — 🏁 LB 0.41457
Qué: subir base-v2 (escala log), que mejoraba 4/4 folds (0.4304 → 0.4154) pero empeoraba el holdout (0.5109 → 0.5244). · Pasó: Kaggle
0.45751 → 0.41457, igual que decían los folds. · Por qué: el holdout es una sola quincena (1-15 ago) y mide sobre todo cómo le va al modelo
en esos días concretos; 4 folds promedian el ruido. Lección: una ventana de validación sola puede engañar; varias, mucho menos.

### v0.1 · primer envío a Kaggle (calibración) — 🏁 LB 0.45751
Qué: subir la base sin mejorar para comprobar si la validación local predice el leaderboard. · Pasó: backtest 0.4745, holdout 0.5191,
Kaggle 0.45751: el test se parece al backtest, no al holdout. · Por qué: los 16 días del holdout (1-15 ago, con la paga del 15) son
especialmente difíciles para una media plana; una sola ventana engaña, por eso usamos 4 folds. El backtest es fiable para decidir.

### base-v0 · media de los últimos 14 días — 📏 LÍNEA BASE (RMSLE 0.4745 ± 0.0090)
Qué: medir la predicción más simple (media de 14 días por tienda×familia) en los 4 folds. · Pasó: 0.4738 / 0.4611 / 0.4769 / 0.4864; muy estable entre folds
(el modelo no tiene aleatoriedad, así que una sola ejecución basta). · Por qué: no conoce el día de la semana ni festivos ni promociones; ese es el margen
que las variantes deben recortar. Cualquier variante debe bajar de 0.4745.

### V-002 · media y perfil semanal en escala log — ✅ ACEPTADA (RMSLE 0.4304 → 0.4154, mejora 4/4 folds)
Qué: promediar log1p(ventas) en vez de ventas (14 d) y sumar el perfil del día de la semana también en log; luego expm1. · Pasó: mejora 4/4 folds (−0.009 a −0.020), sesgo log medio +0.015; sobre todo en LIQUOR/WINE/BEER (−0.050); empeora algo PRODUCE (+0.009).
Por qué: la métrica RMSLE es un error en log, así que promediar en log la alinea con ella y trata mejor los ceros e intermitentes. Modelo determinista: otra semilla da lo mismo. (Nota: se midió contra base-v1; el código parte de base-v0 y no usa el perfil multiplicativo de V-001.)

### V-001 · perfil por día de la semana — ✅ ACEPTADA (RMSLE 0.4745 → 0.4304, mejora 4/4 folds)
Qué: multiplicar la media de 14 días por un factor del día de la semana (media de ese día / media global, últimas 8 semanas, por tienda×familia). ·
Pasó: 0.4368 / 0.4143 / 0.4283 / 0.4423 (−0.044 de media); mejoran todas las familias grandes (LIQUOR/WINE/BEER −0.205, PRODUCE −0.153), empeoran
ligeramente BABY CARE +0.024 y HOME APPLIANCES +0.017. Modelo determinista: una semilla basta. · Por qué: la venta semanal tiene un ciclo fuerte
(fin de semana) que la media plana ignora; el error era sistemático, no ruido.

### V-005 · promociones como rasgos del LightGBM — ✅ ACEPTADA (RMSLE 0.4057 → 0.3946, mejora 4/4 folds)
Qué: V-004 + 3 rasgos (onpromotion del día objetivo, suma 14 d previos al corte, ratio día/media). · Pasó: 0.3949 / 0.3860 / 0.3918 / 0.4057;
otra semilla 0.3940 (variación ~0.001). Mejoran SCHOOL AND OFFICE −0.081, BEAUTY −0.056; ninguna familia empeora más de +0.005. Vs V-003: −0.063. ·
Por qué: el árbol aprende la respuesta a la promo por familia/tienda y no la mezcla con tendencia, que era el fallo de la beta fija de V-003.

### V-004 · LightGBM global con rasgos de la fecha de corte — ✅ ACEPTADA (RMSLE 0.4154 → 0.4057, mejora 3/4 folds)
Qué: un solo LightGBM para las 1782 series, entrenado con 8 cortes pasados (medias log 3/7/14/28/56 d, perfil semanal, h, dow, tienda y familia). ·
Pasó: 0.4041 / 0.3926 / 0.4007 / 0.4255 (f4 +0.003); otra semilla: 0.4046 (variación ~0.001). Empeoran SCHOOL AND OFFICE +0.042 y LIQUOR +0.023;
mejoran HARDWARE −0.033, AUTOMOTIVE −0.031. 15 s. · Por qué: un modelo global comparte información entre series (aprende cómo reacciona cada familia a su
nivel reciente) y una media por serie no lo ve. Aún sin promos, festivos ni anual: margen de mejora.
(*Modelo global*: un único modelo para muchas series, en vez de uno por serie.)

### V-003 · ajuste log por promociones (beta por familia) — ❌ RECHAZADA (RMSLE 0.4154 → 0.4571, empeora 4/4 folds)
Qué: sumar beta_familia·(log1p(promo día) − log1p(promo media 14 d)) a la predicción de V-002. · Pasó: 0.4311 / 0.4405 / 0.4625 / 0.4945;
mejoran BEAUTY −0.057 y SCHOOL −0.041, pero PRODUCE +0.394, DELI +0.241, POULTRY +0.229. Determinista (otra semilla idéntica). ·
Por qué: la beta por regresión mezcla promo con otros efectos (la promo suele coincidir con estacionalidad/tendencia) y en familias de frescos
saca ajustes grandes y erróneos. Si se reintenta: beta solo en familias donde sea significativa o dejar que lo aprenda el LightGBM (V-004).

<!-- Formato:
### V-001 · perfil por día de la semana — ✅ ACEPTADA (RMSLE 0.52 → 0.47, mejora 4/4 folds)
Qué: … · Pasó: … · Por qué: …
-->

## Glosario

- **Serie temporal**: valores medidos en orden en el tiempo (ventas por día). El orden importa: no se pueden barajar las filas.
- **Horizonte**: cuántos pasos hacia delante predecimos. Aquí 16 días. Predecir el día 16 es más difícil que el día 1.
- **Backtesting (validación temporal)**: simular el pasado. Me coloco en una fecha, entreno solo con lo anterior y predigo lo siguiente.
- **Fold**: cada una de esas simulaciones. Usamos 4 para no fiarnos de una sola quincena.
- **Holdout**: un trozo de datos que se guarda sin mirar hasta el final, como examen; si lo usas para decidir, deja de ser examen.
- **Fuga de información (leakage)**: el modelo usa algo que no tendría al predecir de verdad (ventas futuras, transacciones del día).
  Síntoma típico: validación espectacular y test malo.
- **RMSLE**: error cuadrático medio sobre `log(1+y)`. Mide errores relativos (×2 cuesta igual en 10 que en 10.000 unidades).
- **Línea base (baseline)**: el modelo más simple razonable. Sirve de vara de medir: lo que no le gana, no aporta.
- **Estacionalidad**: patrón que se repite (semana, mes, año).
