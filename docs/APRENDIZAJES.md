# Aprendizajes

Bitácora de experimentos: 2-3 líneas por experimento cerrado (**qué se probó · qué pasó · por qué**), del más reciente al más antiguo.
Los conceptos nuevos se explican en el [glosario](#glosario) la primera vez que aparecen.

## Experimentos

### base-v0 · media de los últimos 14 días — 📏 LÍNEA BASE (RMSLE 0.4745 ± 0.0090)
Qué: medir la predicción más simple (media de 14 días por tienda×familia) en los 4 folds. · Pasó: 0.4738 / 0.4611 / 0.4769 / 0.4864; muy estable entre folds
(el modelo no tiene aleatoriedad, así que una sola ejecución basta). · Por qué: no conoce el día de la semana ni festivos ni promociones; ese es el margen
que las variantes deben recortar. Cualquier variante debe bajar de 0.4745.

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
