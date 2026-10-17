# Revisión de rumbo (T-030) — 2026-10-17

Para quien aprende: qué tal vamos, qué hacemos bien/mal y qué cambiaría. **Aviso de honestidad:** la búsqueda web de esta
tarea no encontró los textos originales de los puestos 1.º de Store Sales ni del 1.º de Favorita 2018 (Kaggle no es accesible desde la herramienta).
Lo que sigue combina lo confirmado (con fuente) y mi conocimiento previo, marcado como *(no verificado)*.

## 1. ¿Dónde estamos frente al leaderboard?

- Nuestro LB público: **0.41341** (base-v3). Línea base ingenua (media 14 d): 0.4575.
- Referencias *(no verificado, de memoria de notebooks públicos)*: los mejores del LB de Store Sales están en torno a **0.37–0.38**; un
  LightGBM/«híbrido» razonable de notebook público ronda **0.39–0.45**. Es un LB «Getting Started» continuo, con mucha gente compartiendo
  trucos y algunos usando información del test, así que el techo real no es comparable con una competición cerrada.
- Lectura: **0.413 es un resultado sólido para un modelo limpio sin trucos**; el hueco hasta lo mejor (~0.04) es pequeño en relación
  con lo ya ganado (0.4575 → 0.413). Cada 0.01 cuesta ya mucho más. Con el objetivo de *aprender*, no hay motivo para perseguir el LB.
- Contexto de otras competiciones: el 1.º de Favorita 2018 fue un ensemble de GBM y redes neuronales; el 5.º usó 16 LightGBM (uno por día
  de horizonte) + CNN/DNN + seq2seq y promedio ponderado ([foro fast.ai, 5.º puesto](https://forums.fast.ai/t/5th-place-solution-of-favorita-grocery-sales-forecasting/10009),
  [revisión «Kaggle forecasting competitions»](https://arxiv.org/pdf/2009.07701)). En M5 ganaron LightGBM con rasgos de retardos y varios
  modelos por horizonte ([réplica ODSC](https://opendatascience.com/?p=42726)). Es decir: **nuestro camino (GBM global + rasgos) es el camino
  estándar**; lo que añaden los ganadores es *ensemble* y volumen de entrenamiento, no una idea radicalmente distinta.

## 2. Método: qué hacemos bien y qué mal

**Bien**
- Backtest temporal, holdout intocable y código que impide ver el futuro: es lo más importante y está hecho.
- Criterio fijado antes de medir, comparación fold a fold, semillas repetidas, rechazos documentados (V-003, V-007 enseñan tanto como los aciertos).
- Una variante = un cambio; quien implementa no evalúa.
- Diagnóstico serio del salto CV→LB (T-027) en vez de ignorarlo.

**Mal / mejorable**
1. **Los 4 folds son consecutivos (28-may a 30-jul) y de una sola estación.** No ven vuelta al cole, diciembre, Carnaval ni el tipo de cola
   del test. Es el fallo de método más grave: el CV premió v3 por −0.025 y el LB solo −0.001. Mientras no cambie, cada «mejora» es válida
   *solo para junio-julio*. (T-032 lo ataca; yo lo subiría a prioridad alta y lo haría **antes** de cualquier V-xxx nueva.)
2. **Variantes encadenadas** (V-005 sobre V-004, V-006 sobre V-005): bien para aprender, pero los pasos de −0.004 (V-006) están cerca del ruido
   entre ventanas (una ventana mueve ±0.05; ver T-027). Con folds de una sola estación, esos pasos pequeños no son concluyentes.
   Regla útil: **mejora < 0.005 solo se acepta si gana en ≥ 6 folds de estaciones distintas**.
3. **Criterio «4 folds de 4» es demasiado laxo con 4 folds** correlacionados (casi el mismo periodo): ganar 4/4 es menos informativo de lo que parece.
4. **Holdout = 1-15 ago** y ya se usó para juzgar (v0.2). Está bien como examen, pero con una sola ventana no sirve para decidir.
5. El LB público son 16 días: no usarlo como juez (hay ±0.05 de ruido por ventana). Mejor confiar en un CV ampliado.
6. Falta una **referencia de ruido**: ¿cuánto cambia el RMSLE de un modelo igual con otra semilla Y otra ventana? Ya hay datos (T-027) y conviene ponerlos en el README.

## 3. Cambios de enfoque, ordenados por (ganancia × aprendizaje) / coste

| # | Cambio | Ganancia esperada | Coste | Aprendizaje | Nota |
|---|---|---|---|---|---|
| 1 | **CV ampliado**: 6–8 folds en estaciones distintas (ago-2016 vuelta al cole, dic, feb-Carnaval, may…) + arreglar `start` del 26-dic | 0 en RMSLE, pero evita decidir mal | CPU, minutos | Muy alto (qué es generalizar) | Es T-032; sin esto lo demás se mide mal |
| 2 | **Más cortes de entrenamiento y peso a lo reciente** (8 → 24–40 cortes semanales; peso decreciente) | −0.003…−0.010 *(estimado)* | CPU, ~1–3 min/fold | Alto (cantidad de datos vs frescura) | Palanca clásica de Favorita/M5; barata |
| 3 | **Ensemble ligero**: mezcla de base-v3 con base-v2 (estadística robusta) y de semillas/ventanas | −0.003…−0.008 *(estimado)*; reduce el riesgo de extrapolar (pico de promos) | CPU, segundos | Alto (por qué promediar modelos distintos funciona) | v2 falla distinto a v3: diversidad gratis |
| 4 | **Robustez de rasgos** (V-011: acotar promo al rango visto) y festivos/Carnaval como rasgos | recupera parte de lo perdido en el LB (T-027 estima ≈0.025 del pico del 16-ago) | CPU, minutos | Medio-alto (extrapolación en árboles) | Ya en tablero |
| 5 | **Ajuste básico del LightGBM** (hojas, rondas, lr, `min_data`) | −0.002…−0.006 | CPU, minutos | Medio | Parámetros hoy copiados de ceshine, sin afinar |
| 6 | Modelos por horizonte / recursivo (T-021, T-022) | ±0.003 | ×16 CPU | Medio (estrategias multi-paso) | Bajo retorno aquí: el error casi no crece con `h` (0.454 → 0.498) |
| 7 | statsforecast (ETS/ARIMA) | solo útil como pieza del ensemble; solo por sí mismo ≈ base-v2 o peor *(estimado)* | CPU, pero **requiere instalar** el paquete | Medio | Con 1 782 series diarias de estacionalidad semanal, AutoETS/MSTL tarda minutos; no aportará más que v2 en el mezclado |
| 8 | Redes globales (N-BEATS/TFT/MLP) | incierta; en Favorita sumaron al ensemble, no ganaron solas | GPU (horas de las ~19 h/mes) o CPU lenta; **requiere torch** | Alto como tema, bajo como retorno | Dejar para el final, solo si sobran horas de GPU |
| 9 | Reconciliación jerárquica (tienda/familia/total) | pequeña con RMSLE por serie | CPU | Medio | Se usa cuando importa el total; aquí pesa cada serie igual. No priorizar |

Descartado a la vista de los datos propios: «predecir 0 si N días a 0» (medido ≈0) y hurdle de ceros (el L2 sobre log1p ya estima la media óptima; el 21 % del error de ceros es ruido de ventas pequeñas, no un fallo estructural).

## 4. Tarjetas existentes

- **T-021 (V-008, 16 modelos por horizonte):** bajar a prioridad baja o cancelar. Coste ×16 y el error por horizonte casi plano: poca ganancia posible. Se queda como «aprendizaje», no como mejora.
- **T-022 (V-009, recursivo + promedio):** cancelar por ahora. Hay que reconstruir rasgos día a día (60 min) para un −0.002…−0.01 con riesgo de acumular error.
- **T-023 (V-010, ensemble de semillas y ventanas):** **mantener y adelantar**; es el cambio #3. Añadir al criterio el uso de base-v2 como segundo miembro (ver V-013 abajo) y medirlo en el CV ampliado.
- **T-020 (V-007 tweedie):** ya cerrada; correcta.
- **T-032 (CV ampliado) y T-031 (V-011):** subir T-032 a **alta y primera de la cola**.
- Nuevas (abajo): V-012, V-013, V-014. T-025/T-024/T-033 (infraestructura) no cambian.

## Tarjetas creadas

- V-012: más cortes de entrenamiento + peso a lo reciente.
- V-013: mezcla ponderada base-v3 + base-v2.
- V-014: afinado básico de hiperparámetros del LightGBM.

Todas se miden con el CV ampliado de T-032 si ya existe; si no, con los 4 folds *y* con el fold de control de ago-2016.

## Fuentes

- [5th place, Favorita Grocery Sales Forecasting (fast.ai)](https://forums.fast.ai/t/5th-place-solution-of-favorita-grocery-sales-forecasting/10009)
- [Kaggle forecasting competitions: an overlooked learning opportunity](https://arxiv.org/pdf/2009.07701)
- [Réplica de solución GBM de M5 (ODSC)](https://opendatascience.com/?p=42726)
- [Seq2seq sobre Favorita, RMSLE ≈ 0.54 (arXiv)](https://arxiv.org/abs/2204.07786v1)
- Internos: docs/ANALISIS-ERRORES.md (T-027), docs/DISENO-MODELOS.md, eval/results.
