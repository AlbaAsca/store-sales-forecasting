# Diseño de modelos — qué hacen otros y qué nos falta

Lo mantiene el **modelador**: lee *código* de soluciones de referencia y lo traduce a variantes `V-xxx` de una sola idea.
No se borra nada: cada ronda añade una sección con fecha. Estado: ✅ probado y aceptado · ❌ probado y rechazado ·
🧪 contrafactual (medido en `ANALISIS-ERRORES.md`, sin variante) · 🃏 tarjeta creada · — pendiente.

## 2026-10-15 · ronda 1 (base vigente: base-v2 = V-002, RMSLE 0.4154)

### Código leído

Descargado con `kaggle kernels pull` en `data/kaggle-code/` (fuera de git; código extraído a `.py` para leerlo):

| Ref | Qué es | Lo que importa del código |
|---|---|---|
| [chongzhenjie/ecuador-store-sales-global-forecasting-lightgbm](https://www.kaggle.com/code/chongzhenjie/ecuador-store-sales-global-forecasting-lightgbm) | LightGBM **global** con darts (Store Sales) | `log1p` en el pipeline; `lags` 7/63/365/730 → **4 modelos promediados**; covariables pasadas solo con retardo ≥16 (`range(-16,-23,-1)`); `zero_fc_window=21` (21 días a 0 → predice 0); entrena con todo y con `drop_before="2015-01-01"` y promedia; ceros falsos de días cerrados (1 ene) → NaN. Recursivo (`output_chunk_length=1`). |
| [ceshine/lgbm-starter](https://www.kaggle.com/code/ceshine/lgbm-starter) | Kernel base de casi todo el top de **Favorita 2018** | Objetivo `log1p`, L2. Rasgos calculados **en la fecha de corte**: media 3/7/14 días, promos de los 14 días previos y `promo_i` de cada día futuro. **16 modelos directos** (uno por día del horizonte). Entrena **apilando 4 cortes semanales** (`t2017 + 7·i`). Peso 1.25 a perecederos (la métrica de Favorita lo pedía). |
| [Favorita 5.º puesto (fast.ai)](https://forums.fast.ai/t/5th-place-solution-of-favorita-grocery-sales-forecasting/10009) | Write-up | Ventanas deslizantes de distinta longitud → rasgos; 16 LightGBM directos + CNN + seq2seq, media ponderada. |
| [ekrembayar/…comprehensive-guide](https://www.kaggle.com/code/ekrembayar/store-sales-ts-forecasting-a-comprehensive-guide) | Guía Store Sales | Series que siempre son 0 → predicción 0 fija; medias móviles y EWM **desplazadas ≥16** (`shift(16)`, α 0.5–0.95) para no usar lo que no se conoce. |
| [ferdinandberr/darts-…-global-models](https://www.kaggle.com/code/ferdinandberr/darts-forecasting-deep-learning-global-models) | NN globales con darts | Un modelo por **familia** sobre las 54 tiendas; `log1p`+escalado; covariables futuras (festivos, promo, petróleo) y pasadas (transacciones, medias de ventas); ensamblado. Caro (GPU). |
| [ryanholbrook/exercise-forecasting-with-machine-learning](https://www.kaggle.com/code/ryanholbrook/exercise-forecasting-with-machine-learning) | Curso Kaggle | Estrategia **directa vs recursiva** para 16 pasos (`MultiOutputRegressor`, `RegressorChain`). |
| M5: [m5-methods](https://github.com/umitkaanusta/m5-methods) · [resumen](https://medium.com/analytics-vidhya/predicting-the-future-with-learnings-from-the-m5-competition-d54e84ca3d0d) | Ganadores M5 | 1.º: promedio de LightGBM **directos y recursivos** entrenados por tienda / tienda×categoría / tienda×dpto.; objetivo **tweedie** muy común (ventas con muchos ceros). |
| [mlforecast lag_transforms](https://nixtlaverse.nixtla.io/mlforecast/lag_transforms) | Librería Nixtla | `lags` + `lag_transforms={lag: [RollingMean(w), ExpandingMean()]}`: rasgos de ventana definidos sobre un retardo; `cross_validation` = mismo esquema de cortes que nuestro `folds.json`. |

### Mapa de técnicas (de simple a complejo)

Estado actualizado el 2026-10-17 según el panel.

| # | Técnica | Dónde la vi | Qué hacemos hoy | Cambio propuesto | Ganancia esperada | Coste CPU | Qué se aprende | Estado |
|---|---|---|---|---|---|---|---|---|
| 1 | Perfil por día de la semana | Holbrook (seasonality), ceshine (`mean_4_dow`) | base-v1: factor ×dow por tienda×familia | — | −0.044 | s | Estacionalidad semanal | ✅ V-001 |
| 2 | Trabajar en `log1p` | todos (ceshine, chongzhenjie, darts) | V-002: media y perfil en log | — | −0.015 | s | Alinear con la métrica | ✅ V-002 |
| 3 | Predecir 0 si N días a 0 | chongzhenjie (21 d), ekrembayar | La media ya da 0 | Nada | ≈0 (medido) | s | Por qué una regla «obvia» no aporta | 🧪 sin ganancia |
| 4 | Mezclar ventanas (7d+14d) | ceshine (3/7/14), chongzhenjie (ensemble de lags) | 14 d | Nada como heurística; entra como rasgos en #6 | −0.0003 (medido) | s | Promediar ventanas aporta poco *a mano* | 🧪 |
| 5 | Promos (heurística de elasticidad) | ceshine (`promo_i`, `promo_14`) | Ignoradas | Ya en V-003 | −0.005…−0.01 | s | Covariable futura conocida | ❌ V-003 |
| 6 | **Modelo global LightGBM directo** con rasgos en la fecha de corte | ceshine, Favorita 5.º, chongzhenjie | Una media por serie | Un único LightGBM para las 1 782 series; rasgos = medias log 3/7/14/28/56 d, perfil dow log, `h`, dow, tienda/familia categóricas; objetivo log1p+L2; entrena apilando 8 cortes semanales anteriores | −0.01…−0.03 | ~1 min/fold | Modelo global: aprender de todas las series a la vez; cómo construir el set de entrenamiento sin fuga | ✅ V-004 |
| 7 | Promos como rasgos del GBM | ceshine, darts | — | Sobre #6: `onpromotion` del día objetivo, suma promos 14 d pasados, ratio | −0.005…−0.015 | ~1 min/fold | Covariables futuras en un modelo global vs heurística (comparar con V-003) | ✅ V-005 |
| 8 | Estacionalidad anual (retardo 364) | chongzhenjie (lags 365/730), SMA `shift(365)` ekrembayar | Nada (vuelta al cole falla, ver ANALISIS-ERRORES) | Sobre #6: media log del mismo tramo hace 364 días (alineado por dow) y su ratio frente a la media 14 d de entonces | −0.003…−0.01 (más en test de agosto: vuelta al cole Sierra) | ~1 min/fold | Rasgos de año anterior; señal que ninguna media reciente ve | ✅ V-006 |
| 9 | 16 modelos directos (uno por `h`) vs uno con `h` como rasgo | ceshine, Favorita 5.º | — | Variante de #6 | ±0.003 | ×16 | Estrategias multi-paso | ❌ V-008 |
| 10 | Recursivo vs directo, y promedio de ambos | Holbrook, M5 1.º, chongzhenjie | — | Tras #6 | −0.002…−0.01 | ×2 | Acumulación de error recursivo | ✅ V-009 (media) |
| 11 | Objetivo tweedie sobre ventas crudas | M5 (muy usado) | — | Variante de #6 cambiando solo el objetivo | ±0.005 (RMSLE ya premia log+L2) | igual | Elegir pérdida según la métrica | ❌ V-007 |
| 12 | Festivos/paga/petróleo como rasgos | darts, chongzhenjie | — | Sobre #6 | ≈0 en folds (no hay festivos nacionales, ver ANALISIS-ERRORES) | igual | Saber cuándo una covariable no puede ayudar en tu validación | 🃏 V-016/V-017 (ronda T-041) |
| 13 | Ensemble de semillas / ventanas de entrenamiento (todo vs desde 2015) | chongzhenjie | — | Tras #6–#8 | −0.002…−0.005 | ×2–×4 | Reducir varianza | ❌ V-010 |
| 14 | Redes globales (N-BEATS, TFT, seq2seq) | darts, Favorita 5.º | — | Solo si GBM se estanca; GPU Kaggle | incierta | GPU (horas) | Deep learning para series | — |

### Notas para el desarrollador (comunes a V-004…V-006)

- **Sin fuga al construir el entrenamiento**: los cortes de entrenamiento `t_k = corte − 16 − 7·k` (k = 0…7); el objetivo de cada
  corte son los 16 días `[t_k, t_k+15]`, que acaban **antes** del corte del fold. Los rasgos solo usan fechas `< t_k`.
- En predicción se calculan los mismos rasgos en el corte real. `h` = 1…16, días desde el corte.
- `lightgbm` ya está en `requirements.txt` (4.7). Semilla desde `ctx["seed"]`; repetir con otra semilla (CLAUDE.md, regla 3).
- Parámetros de partida (ceshine): `num_leaves=31, learning_rate=0.05, min_data_in_leaf=50, feature_fraction=0.75,
  bagging_fraction=0.75, bagging_freq=1`, ~300–500 rondas fijas (no hay set de validación dentro del fold; no usar el fold para
  early stopping). Predicción: `expm1`, `clip(0)`.

## 2026-10-17 · T-041 · variables nuevas: festivos, día de paga y vuelta al cole (base vigente: base-v4, CV 0.3858)

**Por qué ahora.** V-010, V-012, V-013 y V-014 movieron el mismo modelo con los mismos datos y no ganaron más que la variación
de semilla (~0.001). El siguiente salto tiene que venir de **información que el modelo todavía no ve**. Hoy base-v4 solo sabe del
calendario el día de la semana (`dow`) y el horizonte (`h`): no sabe qué día del mes es, si es festivo en la ciudad de la tienda,
ni ha visto nunca en entrenamiento un arranque de temporada escolar.

### Medido antes de proponer (predicciones de `eval/results/base-v4/`, sin tocar el holdout)

1. **El control c1 (0.755) NO es la vuelta al cole: son dos tiendas que cierran.** La tienda 18 vende 0 desde el 15-ago-2016
   (todo c1) y la 25 desde el 22-ago (a mitad de ventana). Juntas aportan el **74 %** del error cuadrático de c1; SCHOOL AND OFFICE
   solo el 2.3 %. **Sin las tiendas 18 y 25, c1 = 0.3902**, en línea con los folds (de ahí que el error de c1 suba a partir del
   22-ago). Un cierre no se puede prever con datos anteriores al corte. Consecuencia: «no empeorar c1» hay que leerlo **sin tiendas
   cerradas**, o el ruido de los cierres tapa cualquier efecto (tarjeta de herramienta aparte para el arquitecto).
2. **Día de paga: hay sesgo sistemático por día del mes.** Sesgo medio log(pred/real) en los 4 folds: días 15-16 +0.010,
   fin de mes y días 1-2 **−0.044**, días 3-5 **−0.054**, resto +0.018. El modelo se queda corto justo después de cobrar y se pasa
   el resto del mes: es justo lo que un rasgo de día del mes puede corregir. Quitar ese sesgo vale ≈ −0.001 de RMSLE.
3. **Festivos: casi no hay en lo que medimos.** En los folds (28-may…30-jul-2017) solo 9 festivos locales/regionales (≈1 % de
   filas); en el test de Kaggle uno local (Ambato, 24-ago, 2 tiendas); en c1 el mismo. Sí los hay en el **holdout** (10-ago nacional
   *trasladado* al 11-ago) y en los cortes de entrenamiento de f4 (1-may, Día de la Madre 13/14-may, traslado al 26-may).
   Ganancia en CV ≈ 0; donde puede notarse es en el holdout.
4. **Vuelta al cole: el fallo está en f1, no en c1.** SCHOOL AND OFFICE aporta el 8.1 % del error de f1 (RMSLE 0.637; la Sierra
   arranca el 20-jul) y el 6.4 % de f4. El directo se entrena con cortes de las 8 semanas anteriores, que **nunca contienen un
   arranque de temporada**: `ly_diff` le dice «el año pasado aquí hubo un salto», pero no tiene ejemplos de entrenamiento en los que
   ese rasgo importe, así que apenas lo usa.

### Tabla (ordenada por ganancia esperada / coste)

| # | Técnica | Dónde la vi | Qué hacemos hoy | Cambio propuesto | Ganancia esperada | Coste CPU | Qué se aprende | Estado |
|---|---|---|---|---|---|---|---|---|
| 1 | **Día del mes y paga** | [Descripción de los datos](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data) («wages in the public sector are paid every two weeks on the 15th and on the last day of the month»); investigador T-040 | Solo `dow` y `h` | `dom` (1-31), `is_payday` (15 o último día), `dias_desde_paga` (0-15), `dias_a_fin_mes`, en `_features` **y** `_step_feats` | ≈ −0.001 (sesgo de −0.05 en días 1-5 medido arriba) | igual | Cómo un rasgo de fecha corrige un sesgo que el modelo no puede ver | 🃏 V-016 |
| 2 | **Festivo del día objetivo según la tienda** | [chongzhenjie](https://www.kaggle.com/code/chongzhenjie/ecuador-store-sales-global-forecasting-lightgbm) (`process_holiday`: descarta `transferred=True` y `Work Day`; locales por ciudad, regionales por estado, nacionales por fecha) | Nada (`ctx["holidays"]` y `ctx["stores"]` llegan al modelo y no se usan) | 0/1 del día objetivo: `hol_nat`, `hol_reg` (estado de la tienda), `hol_loc` (ciudad), `event_nat`; `transferred=True` = día normal; `Transfer`/`Bridge`/`Additional` = festivo; `Work Day` = laborable | ≈0 en CV; posible mejora en holdout (10-11 ago) | igual | Por qué una covariable no puede ayudar si la validación no la contiene; leer festivos trasladados | 🃏 V-017 |
| 3 | **Cortes de entrenamiento del mismo periodo del año anterior** | ceshine/Favorita (los inicios de entrenamiento se eligen por calendario, `t2017 = date(2017,5,31)` + 7·i, la misma estación que el test) | 8 cortes semanales recientes (V-012 añadió más cortes *recientes* y empeoró) | Añadir al directo 4 cortes en `T − 16 − 364 + 7·j`, j = −1…2 (rodean la fecha de corte de hace un año; sus `ly_*` miran 2 años atrás, hay datos desde 2013) | −0.002…−0.005 si SCHOOL baja en f1; más en el test de Kaggle (Sierra) | ×1.5 filas en el directo | Para que el modelo aprenda un régimen, el entrenamiento tiene que contenerlo | 🃏 V-018 |
| 4 | Limpiar festivos de la historia (que el 10-11 ago no entre en las medias) | Favorita (tratar días anómalos como faltantes) | Nada | Sustituir días festivos nacionales de las ventanas por la media del mismo dow | ≈0 en CV, algo en el test (sus 14 d previos contienen el 10-11 ago) | igual | Los rasgos de entrada también pueden estar contaminados | — (tras V-017) |
| 5 | Región Sierra/Costa × temporada escolar | Calendario escolar de Ecuador | Nada | `region` + `school_season` | se solapa con #3 y es peor medible (los cortes no ven ninguna temporada) | igual | — | — (solo si #3 falla) |

**Orden recomendado**: V-016 (el más barato y con el sesgo ya medido) → V-017 → V-018. Cada una enseña una sola idea; si una
gana, las siguientes se rehacen sobre la nueva base.

### Notas para el desarrollador (V-016…V-018)

- Los rasgos del **día objetivo** (día del mes, festivo) se conocen de antemano: no son fuga. Lo prohibido sigue siendo usar
  ventas o transacciones `>= corte`.
- base-v4 tiene **dos submodelos** (directo `_features` y recursivo `_step_feats`) y promedia: los rasgos de calendario van en los
  dos, si no el efecto se diluye a la mitad. V-018 solo toca el directo.
- Para fechas usa `days.append(fdates)` (igual que `dow_all`); la columna `origin + j` es el día objetivo `j`.
- Criterio común: CV medio < 0.3858, empeora como mucho 1 de 4 folds, mejora > 0.001 (repetir con otra semilla), c1 **sin las
  tiendas 18 y 25** no empeora (hoy 0.3902); anotar el RMSLE de SCHOOL AND OFFICE en f1 y el holdout (lo mide el consultor).
