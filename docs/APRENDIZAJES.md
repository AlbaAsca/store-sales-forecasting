# Aprendizajes

Bitácora de experimentos: 2-3 líneas por experimento cerrado (**qué se probó · qué pasó · por qué**), del más reciente al más antiguo.
Los conceptos nuevos se explican en el [glosario](#glosario) la primera vez que aparecen.

## Experimentos

### v0.3 · tercer envío: el LightGBM mejora mucho en local y casi nada en Kaggle — 🏁 LB 0.41341
Qué: subir base-v3 (LightGBM global + promos + lag 364). · Pasó: backtest 0.4154 → 0.3904 (−0.025) y holdout 0.5244 → 0.4378 (−0.087),
pero Kaggle solo 0.41457 → 0.41341 (−0.001). · Por qué: aún no lo sabemos (tarjeta de diagnóstico). Lección provisional: la validación local
puede dejar de predecir el leaderboard cuando el modelo cambia de tipo; hay que entender la brecha antes de fiarse de la siguiente mejora.

### V-011 · acotar rasgos de promoción al p99 de entrenamiento — ❌ RECHAZADA (CV 0.3904 → 0.3908, semilla 1: 0.3910)
Qué: recortar promo_day y promo_ratio por familia al percentil 99 visto, para que el pico de promos del 16-ago (fuera de rango) no se extrapole. · Pasó: el CV queda igual (folds +0.0020/−0.0004/+0.0002/−0.0005), pero el 16-ago sigue
disparado frente al 17-ago: SCHOOL ×3.06 (antes ×3.29), LAWN ×2.77 (×3.91), LINGERIE ×1.84 (×2.32); el criterio pedía ≤ ×1.5. · Por qué: recortar ayuda algo, pero el salto lo siguen empujando otros rasgos (calendario, retardos); los árboles no extrapolan, así que el problema no era solo el valor extremo de la promo. Idea: atacar el pico por otro lado (p. ej. rasgo de día concreto o tope de predicción).

### V-007 · objetivo tweedie sobre ventas crudas — ❌ RECHAZADA (RMSLE 0.3904 → 0.4094, empeora 4/4 folds)
Qué: cambiar la función de pérdida del LightGBM de L2 sobre log1p(ventas) a tweedie (p=1.3) sobre ventas crudas. · Pasó: 0.4075 / 0.3885 / 0.4113 / 0.4304;
semilla 7 igual (0.4094): la variación es ~0.000, el empeoramiento (+0.019) es real. Peor en LAWN AND GARDEN +0.072, LADIESWEAR +0.046, SEAFOOD +0.043; 3× más lento. ·
Por qué: la función de pérdida es lo que el modelo intenta minimizar al entrenar; si no coincide con la métrica, optimiza otra cosa. RMSLE es L2 en log1p, así que L2 sobre log1p ya es exactamente la métrica. Tweedie pondera por escala (las series grandes mandan) y las familias de pocas ventas pierden.

### V-006 · estacionalidad anual (retardo 364) como rasgo — ✅ ACEPTADA (RMSLE 0.3946 → 0.3904, mejora 4/4 folds)
Qué: a V-005 se le añaden 3 rasgos: log1p de las ventas del mismo día un año antes (−364 d), su ventana ±3 d y la diferencia frente a la media 14 d previa a ese día. ·
Pasó: 0.3932 / 0.3796 / 0.3861 / 0.4029; otra semilla: 0.3903 (variación ~0.001). Mejoran GROCERY I −0.028, HOME CARE −0.022, DAIRY −0.021;
SCHOOL AND OFFICE queda casi igual (media 0.547 → 0.543: peor en f1/f2 ~+0.009, mejor en f3/f4). 24 s. · Por qué: las medias recientes no ven picos anuales;
mirar el mismo día del año anterior aporta esa memoria. Ganancia modesta y estable (≈10× la variación de semilla). El pico escolar sigue sin resolverse (solo hay 1 año previo útil).
(*Retardo (lag)*: valor de la serie de hace N días usado como rasgo.)

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

### v0.2 · segundo envío: ¿a quién creer, a los folds o al holdout? — 🏁 LB 0.41457
Qué: subir base-v2 (escala log), que mejoraba 4/4 folds (0.4304 → 0.4154) pero empeoraba el holdout (0.5109 → 0.5244). · Pasó: Kaggle
0.45751 → 0.41457, igual que decían los folds. · Por qué: el holdout es una sola quincena (1-15 ago) y mide sobre todo cómo le va al modelo
en esos días concretos; 4 folds promedian el ruido. Lección: una ventana de validación sola puede engañar; varias, mucho menos.

### V-003 · ajuste log por promociones (beta por familia) — ❌ RECHAZADA (RMSLE 0.4154 → 0.4571, empeora 4/4 folds)
Qué: sumar beta_familia·(log1p(promo día) − log1p(promo media 14 d)) a la predicción de V-002. · Pasó: 0.4311 / 0.4405 / 0.4625 / 0.4945;
mejoran BEAUTY −0.057 y SCHOOL −0.041, pero PRODUCE +0.394, DELI +0.241, POULTRY +0.229. Determinista (otra semilla idéntica). ·
Por qué: la beta por regresión mezcla promo con otros efectos (la promo suele coincidir con estacionalidad/tendencia) y en familias de frescos
saca ajustes grandes y erróneos. Si se reintenta: beta solo en familias donde sea significativa o dejar que lo aprenda el LightGBM (V-004).

### V-002 · media y perfil semanal en escala log — ✅ ACEPTADA (RMSLE 0.4304 → 0.4154, mejora 4/4 folds)
Qué: promediar log1p(ventas) en vez de ventas (14 d) y sumar el perfil del día de la semana también en log; luego expm1. · Pasó: mejora 4/4 folds (−0.009 a −0.020), sesgo log medio +0.015; sobre todo en LIQUOR/WINE/BEER (−0.050); empeora algo PRODUCE (+0.009).
Por qué: la métrica RMSLE es un error en log, así que promediar en log la alinea con ella y trata mejor los ceros e intermitentes. Modelo determinista: otra semilla da lo mismo. (Nota: se midió contra base-v1; el código parte de base-v0 y no usa el perfil multiplicativo de V-001.)

### V-001 · perfil por día de la semana — ✅ ACEPTADA (RMSLE 0.4745 → 0.4304, mejora 4/4 folds)
Qué: multiplicar la media de 14 días por un factor del día de la semana (media de ese día / media global, últimas 8 semanas, por tienda×familia). ·
Pasó: 0.4368 / 0.4143 / 0.4283 / 0.4423 (−0.044 de media); mejoran todas las familias grandes (LIQUOR/WINE/BEER −0.205, PRODUCE −0.153), empeoran
ligeramente BABY CARE +0.024 y HOME APPLIANCES +0.017. Modelo determinista: una semilla basta. · Por qué: la venta semanal tiene un ciclo fuerte
(fin de semana) que la media plana ignora; el error era sistemático, no ruido.

### v0.1 · primer envío a Kaggle (calibración) — 🏁 LB 0.45751
Qué: subir la base sin mejorar para comprobar si la validación local predice el leaderboard. · Pasó: backtest 0.4745, holdout 0.5191,
Kaggle 0.45751: el test se parece al backtest, no al holdout. · Por qué: los 16 días del holdout (1-15 ago, con la paga del 15) son
especialmente difíciles para una media plana; una sola ventana engaña, por eso usamos 4 folds. El backtest es fiable para decidir.

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
- **Función de pérdida**: la regla con la que el modelo puntúa sus errores mientras aprende (L2 = error² ; tweedie = pensada para datos con muchos ceros y colas largas). Conviene que case con la métrica final: L2 sobre log1p(ventas) es exactamente RMSLE, así que optimiza lo que se evalúa; tweedie sobre ventas crudas optimiza otra cosa (V-007 lo pone a prueba).
