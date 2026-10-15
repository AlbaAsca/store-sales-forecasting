# Aprendizajes

Bitácora de experimentos: 2-3 líneas por experimento cerrado (**qué se probó · qué pasó · por qué**), del más reciente al más antiguo.
Los conceptos nuevos se explican en el [glosario](#glosario) la primera vez que aparecen.

## Experimentos

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
