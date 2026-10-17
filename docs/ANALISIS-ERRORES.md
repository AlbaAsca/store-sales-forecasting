# Análisis de errores

Cómo leerlo: el RMSLE es la raíz de la media de `(log(1+pred) − log(1+real))²`. Ese cuadrado es el «error» de cada fila;
**share** = % del error total que aporta un grupo (si un grupo pesa el 10 % de filas y aporta el 30 % del error, ahí está el
problema). **Sesgo** = media de `log(1+pred) − log(1+real)`: positivo = el modelo predice de más.
Solo folds de `eval/folds.json`; el holdout no se ha mirado.

Scripts (reproducibles): `python scripts/analysis/errors_base.py base-v0` (desglose y casos),
`python scripts/analysis/errors_cf.py` (contrafactuales), `python scripts/analysis/errors_promo.py` (promociones). T-027: `diag_lb_gap.py`, `diag_window.py`.

## 2026-10-17 · T-027 · ¿Por qué base-v3 gana −0.025 en CV y solo −0.001 en Kaggle?

Datos de partida: CV v2 0.4154 → v3 0.3904 · LB público v2 0.41457 → v3 0.41341. Scripts:
`python scripts/analysis/diag_lb_gap.py` (bug, test, ruido; tabla en `scripts/analysis/diag_lb_gap_windows.csv`) y
`python scripts/analysis/diag_window.py <inicio>` (desglose v2/v3 de una ventana). En el holdout solo se comparan
predicciones entre sí; sus ventas reales no se han mirado.

**Veredicto: no es un bug. Es sobre todo un problema de *distribución distinta* en el test de Kaggle (un pico de
promociones el 16-ago que no existe en ningún dato de entrenamiento + vuelta al cole), con algo de mala suerte encima.**

### (1) ¿Bug en la ruta de envío? No
| Comprobación | Resultado |
|---|---|
| Reproducir `make_submission` cortando en 2017-07-30 (future barajado, `family` recategorizada) vs `eval/results/base-v3-holdout` | 0 filas sin pareja, \|Δlog\| máx 4e-16 → idéntico |
| ids de test únicos y crecientes; `dist/*.csv` mismos ids y orden | sí |
| familias y tiendas de test = train; categorías en el mismo orden | sí |
| último día de train completo (1782 series) | sí |

Concepto: **reproducir la ruta de envío** = ejecutar el mismo código que genera el CSV de Kaggle pero en una ventana
donde ya tenemos la predicción del backtest. Si coinciden, el fallo no está en el «fontanero» (ids, orden, tipos).

### (2) Dónde difieren v2 y v3 en el test de Kaggle
RMS de `log(1+v3) − log(1+v2)` = 0.243 (media +0.002: no hay sesgo global). El reparto está muy concentrado:

| Familia | share de la diferencia | media Δlog |
|---|---|---|
| SCHOOL AND OFFICE SUPPLIES | 37 % | +0.11 |
| LINGERIE | 12 % | +0.12 |
| LAWN AND GARDEN | 12 % | +0.07 |
| resto (30 familias) | 39 % | ≈0 |

Por día, el **16-ago** es la anomalía: RMS Δlog 0.615 (los demás días 0.17–0.24). Ese día el test trae un **pico de
promociones fuera de rango**: 30 539 artículos en promo en total (mediana de jun-ago 11 670), y por familia:

| Familia (suma 54 tiendas) | promo 16-ago | promo resto de días | máx. histórico en train | v2 16-ago | v3 16-ago | v3 17-ago |
|---|---|---|---|---|---|---|
| SCHOOL AND OFFICE SUPPLIES | 734 | ~150 | — | 2 242 | **3 887** | 1 182 |
| LAWN AND GARDEN | 842 | 0–184 | 212 | 833 | **2 495** | 638 |
| LINGERIE | 255 | ~50 | — | 320 | **780** | 336 |

v3 tiene `promo_day` y `promo_ratio`; LightGBM extrapola con el valor más alto que vio y **triplica** la venta ese día.
¿Es creíble? En train, los días en que la promo de una familia se multiplica ×4 o más sobre su mediana de 14 días
(1 012 casos, antes del holdout) la venta sube de mediana solo **×1.11**. Si la venta real del 16-ago se parece a la de
v2, esas ~160 filas añaden ≈0.02 de MSE, es decir **≈+0.025 de RMSLE**: del orden exacto de la ganancia que «desaparece».
Es una estimación (no conocemos la venta real), pero es el candidato principal.

Segundo foco, **vuelta al cole (régimen Sierra, septiembre)**: v3 predice para SCHOOL 1 100–1 900 u/día, la mitad que
v2 (2 200–5 300), justo cuando en 2016 la venta subía cada semana (16-ago 656 → 31-ago 833 → 8-sep 1 502 u/día).
Ningún fold de CV (28-may a 30-jul) contiene esta estación, así que el CV no podía premiar ni castigar ese cambio.

### (3) ¿Ruido? En parte
v2 y v3 reentrenados en 23 ventanas de 16 días (jun-2016 a may-2017):

| | valor |
|---|---|
| Δ(v3−v2) mediana | −0.031 (v3 gana en 20/23) |
| ventanas con Δ > −0.005 (como el LB) | 3/23: 26-dic (+0.34), 28-feb (+0.15), 3-may (+0.03) |
| RMSLE de v3 entre ventanas «normales» | 0.39–0.53; con festivos hasta 1.62 |
| ventanas análogas al test (16-ago-2016, 20-ago-2016) | Δ −0.018 y −0.031: en agosto normal v3 sí gana |

Lectura: una sola ventana de 16 días mueve el RMSLE ±0.05 sin cambiar el modelo, y la ventaja v3−v2 varía mucho. Un
−0.001 cae en la cola mala (≈13 % de ventanas), y **todas** las ventanas de esa cola tienen un evento raro. El test
de Kaggle tiene el suyo (el pico de promo), así que encaja con «evento + ruido», no con «v3 no generaliza».

### Hallazgos colaterales (no explican el LB, pero son reales)
- **26-dic-2016**: train no tiene filas del 25-dic, así que `history.max()` = 24-dic y `fit_predict` calcula
  `start` = 25-dic; las fechas predichas van del 25-dic al 9-ene y **el 10-ene queda sin predicción → 0** (sesgo −3.46).
  Afecta solo a ventanas que empiezan el 26-dic (no al test de Kaggle). Arreglo: `start = future.date.min()`.
- **28-feb-2017 (Carnaval)**: v3 predice de menos los domingos (sesgo −0.69 y −0.80) y el martes de Carnaval (−0.46);
  pierde sobre todo en perecederos (PREPARED FOODS, MEATS, POULTRY). v3 es menos robusto que v2 alrededor de festivos.

### Qué hacer
1. Que v3 no extrapole promociones fuera del rango visto (tarjeta V-011).
2. Medir también en un fold de control de finales de agosto de 2016 para que el CV vea la vuelta al cole y no
   volvamos a fiarnos solo de mayo-julio (tarjeta del arquitecto).

## 2026-10-15 · base-v0 (media de 14 días) — RMSLE 0.4745

### Hallazgos (de más a menos importante)

| # | Hallazgo | Evidencia |
|---|---|---|
| 1 | **Predice de más de forma sistemática** (sesgo log +0.098, positivo en los 4 folds). Causa: la media *aritmética* la inflan los días buenos, pero la métrica mide en log y castiga igual pasarse ×2 que quedarse ÷2. | Sin cambiar nada más, usar la media de `log(1+ventas)` (media geométrica) baja de 0.4745 a **0.4545** y el sesgo a ≈0. |
| 2 | **Los ceros cuestan el 22 % del error** en solo el 8 % de filas: días con venta 0 en los que predecimos > 0 (RMSLE 0.80 en esas filas). Las series *intermitentes* (≤50 % de ceros en los últimos 14 días) son el 13 % de filas y aportan el **27 %** del error. | Tabla real0/pred0 y z14_bin. Las series 100 % a cero ya se predicen bien (0.11): poner 0 si los 14 días son 0 no cambia nada porque la media ya es 0. La media en log arregla parte: un día a 0 tira la media en log mucho más que la aritmética. |
| 3 | **Ignora el día de la semana**: de lunes a viernes predice de más (sesgo +0.16…+0.25) y el fin de semana de menos (−0.11/−0.12). | Ya lo ataca V-001 (0.4304, mejora los 4 folds). Mi contrafactual lo reproduce exacto. |
| 4 | Familias peores: LIQUOR,WINE,BEER (0.76), LINGERIE, SCHOOL AND OFFICE SUPPLIES, CELEBRATION; todas de **volumen bajo e intermitente** y todas con sesgo positivo. | Tabla por familia. LIQUOR depende mucho del día de la semana (V-001 la mejora −0.205). |
| 5 | **Horizonte**: el error crece poco con el día (0.454 el día 1 → 0.498 los días 15-16). No es el problema principal. | Tabla por h. |
| 6 | **Días de paga** (15-16, fin de mes, día 1): error *menor* (0.452 vs 0.478). No es un punto débil ahora. | Tabla paga. |
| 7 | **Festivos**: no hay festivos nacionales en los 4 folds (28 may–30 jul 2017); los locales/regionales son el 0.8 % de filas y no destacan. El terremoto (abr 2016) queda fuera de las ventanas de 14 días. | Ojo: el test de Kaggle (16–31 ago 2017) tampoco tiene nacionales; no es prioridad. |
| 8 | **Promociones**: cuando un día tiene más promos que la media reciente, predecimos de menos (sesgo −0.11 con +0.5..2 promos) y al revés (+0.08). Efecto real pero aporta poco error (~25 % del error está en filas con promo distinta, y el sesgo es moderado). | `errors_promo.py` sobre el mejor contrafactual. |
| 9 | El error está **repartido**: el 1 % peor de series aporta solo el 5.8 %; el 10 % peor, el 30 %. No hay 3 series que arreglar a mano. | Ranking de series. |

### Casos concretos (fold f1, 15–30 jul 2017)

- **Tienda 45 × SCHOOL AND OFFICE SUPPLIES** (la serie que más error aporta). Vendía ~5/día; el 20 de julio arranca la
  **vuelta al cole de la Sierra** (Quito) y salta a 100–750/día. Predecimos 4.36 plano: error de hasta −4.9 en log.
  Ninguna media reciente puede verlo; haría falta estacionalidad anual (mismo periodo del año anterior). Solo afecta a una
  familia y a unas semanas → anotado, no priorizado.
- **Tienda 44 × GROCERY I** (gran volumen). Patrón semanal claro: sáb/dom ~14 000, jue ~7 500; predecimos 11 171 todos los
  días → +0.44 el jueves, −0.26 el domingo. Es exactamente lo que arregla el perfil semanal (V-001).
- **Tienda 1 × BEVERAGES**. Patrón invertido: el **domingo** vende la mitad (~1 100 frente a ~2 300; tienda de oficinas en
  Quito). Error +0.73/+0.78 cada domingo. Confirma que el perfil semanal tiene que ser **por tienda×familia**, no global.

### Contrafactuales (calculados solo con datos anteriores al corte)

| Predicción | f1 | f2 | f3 | f4 | media |
|---|---|---|---|---|---|
| base-v0: media 14d | 0.4738 | 0.4611 | 0.4769 | 0.4864 | 0.4745 |
| V-001: media 14d × perfil semanal | 0.4368 | 0.4143 | 0.4283 | 0.4423 | 0.4304 |
| media log 14d | 0.4569 | 0.4483 | 0.4530 | 0.4599 | 0.4545 |
| **media log 14d + perfil semanal en log** | 0.4201 | 0.4057 | 0.4138 | 0.4222 | **0.4154** |
| media log 7d + perfil log | 0.4247 | 0.4149 | 0.4220 | 0.4293 | 0.4227 |
| log (7d+14d)/2 + perfil log | 0.4183 | 0.4068 | 0.4137 | 0.4215 | 0.4151 |

«Perfil en log» = para cada tienda×familia×día de semana, media de `log(1+ventas)` de ese día menos la media de las
8 semanas; se *suma* en log (equivale a multiplicar, pero promediando en la misma escala que la métrica).

### Conclusión

El error más grande y barato de arreglar es **promediar en la escala equivocada** (hallazgos 1 y 2): la métrica es en log y
la base promedia en ventas. Pasar todo a log mejora V-001 en −0.015 en los 4 folds. Mezclar 7d y 14d apenas añade
(−0.0003): no merece variante propia. Siguiente en tamaño: promociones (hallazgo 8). Estacionalidad anual (vuelta al cole)
y modelos de árboles para series intermitentes quedan para más adelante.
