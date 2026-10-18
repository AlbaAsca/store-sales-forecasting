# Brainstorming para base-v10

## 1/3 · Modelador: qué hacen las soluciones top que nosotros no (2026-10-18, T-089)

Base vigente: **base-v9** (= V-031: 3 historiales 14/56/364 d × directo+recursivo, promos de días vecinos, año anterior sin
cierres, cero en series muertas). Prácticas 0.3814 / 0.3815, ~430 s por medición y semilla.

**Descartado de entrada** (ya probado y rechazado, ver `APRENDIZAJES.md`): tweedie (V-007, V-032), 16 modelos por horizonte (V-008),
más semillas/copias (V-010, V-021), más cortes recientes con peso (V-012), afinado (V-014), intermitencia (V-015, V-022), día de paga
(V-016), festivos (V-017), reparto directo/recursivo (V-020), agregados tienda/familia (V-028), un modelo por familia (V-029),
cuantiles (V-033), reconciliación (V-034). Tampoco propongo transacciones: solo se conocen en el pasado y son un agregado de tienda,
lo mismo que falló en V-028.

**Código releído** (`data/kaggle-code/`): [chongzhenjie](https://www.kaggle.com/code/chongzhenjie/ecuador-store-sales-global-forecasting-lightgbm)
(ceros de tienda cerrada tratados aparte, l. 111-141; recorte de historia `drop_before`), [ekrembayar](https://www.kaggle.com/code/ekrembayar/store-sales-ts-forecasting-a-comprehensive-guide)
(`ewm_features`, l. 479-491: medias exponenciales α 0.5…0.95), [ceshine/lgbm-starter](https://www.kaggle.com/code/ceshine/lgbm-starter) y
[Favorita 1.º](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/discussion/47582) (días hasta/desde promo, promos
de 60/140 d, cortes elegidos por calendario), [mlforecast target_transforms](https://nixtlaverse.nixtla.io/mlforecast/docs/how-to-guides/target_transforms_guide.html)
(normalizar el objetivo por serie antes de entrenar).

**Huecos de base-v9 frente a ese código.** (1) Un día con la tienda cerrada (25-dic sin fila → `fillna(0)`, 1-ene, cierres de las tiendas
18/25 en 2016, días antes de abrir una tienda) entra en las medias y en los rasgos `ly_*` como venta 0 real. En concreto, en el test de
Kaggle (16-31 ago 2017) `ly_day/ly_win` de las tiendas 18 y 25 leen el cierre de agosto 2016: V-025 limpió los *cortes* de entrenamiento,
pero no los *rasgos* de predicción. (2) Todas nuestras medias pesan igual cada día de la ventana; nadie le da más peso a ayer que a hace
dos semanas. (3) De las promos futuras sabemos el día, el anterior, el siguiente y la suma, pero no «cuánto falta para la próxima» ni
el historial largo de promos. (4) Solo hay **una** vuelta al cole previa en el entrenamiento (2016). (5) El árbol predice el nivel
absoluto en log; no puede extrapolar fuera de lo visto.

| # | Idea | Hipótesis | Cambio concreto (uno solo) | Ganancia esperada | Coste (min) | Riesgo |
|---|---|---|---|---|---|---|
| 1 | **Días de tienda cerrada como dato que falta** | Un cero por cierre no es «no se vendió», es «no hubo tienda»; meterlo en las medias baja el nivel y en `ly_*` lleva el cierre de 2016 al test | Antes de calcular rasgos: en `M`, poner NaN en los días en que la tienda entera vende 0 (incluye 25-dic y días antes de su primera venta) y usar medias que ignoran NaN (`nanmean`); objetivos de entrenamiento sin tocar | −0.0005…−0.002 en prácticas; algo más en Kaggle (tiendas 18/25 y el 1-ene no afecta al test) | 25 impl. + 35 medir | Bajo de fuga (solo pasado). Cuidado: la regla del cero (V-023) debe seguir viendo ceros reales, aplicarla sobre la `M` original. Mirar control sin cerradas |
| 2 | **Medias con más peso a lo reciente** | Una media exponencial reacciona antes a cambios de nivel que la de ventana fija; es el rasgo estrella de ekrembayar y de Favorita 1.º | Añadir `ewm_a05`, `ewm_a08`, `ewm_a095` (media exponencial de log1p hasta el corte, α 0.5/0.8/0.95) en `_features` y `_step_feats` | −0.0003…−0.001 | 20 + 35 | Puede ser redundante con las 3 ventanas (como V-015); si queda bajo el ruido, se rechaza sin pena |
| 3 | **Distancia a la próxima y a la última promo** | La gente espera a una promo que sabe que viene o se ha abastecido en la anterior; V-027 ya mostró que los días vecinos importan | Rasgos `dias_a_prox_promo` y `dias_desde_promo` (0-16, NaN si ninguna en la ventana conocida) y `promo_sum60` en los dos submodelos | −0.0005…−0.0015 | 25 + 35 | Bajo: la promo del test es conocida. Que entrenamiento y predicción vean la misma ventana (no mirar más allá del día 16) |
| 4 | **Dos vueltas al cole en el entrenamiento** | V-018/V-025 ganaron al enseñar *un* arranque de temporada; con dos años (2015 y 2016) el patrón es menos dependiente de las rarezas de un solo año | Añadir al directo los mismos 4 cortes de V-025 pero a −728 d (`T − 16 − 728 + 7·j`), con el mismo filtro de tiendas cerradas | −0.0005 en prácticas (f1 escolar); más en Kaggle (agosto) | 15 + 35 | Medio: anomalías de 2015 viajan al test (lección v0.6); su `ly_*` mira a 2014. Revisar tiendas del test frente a base-v9 antes de subir |
| 5 | **Predecir la diferencia con el nivel reciente** | El árbol no extrapola: si una serie sube por encima de lo visto, se queda corto. Predecir «cuánto se aparta de su media de 14 días» le quita ese límite (mlforecast lo hace con `target_transforms`) | Solo en el directo: objetivo = log1p(venta) − m14 en el corte; en predicción se le suma m14 | ±0.003 (incierta) | 20 + 35 | Medio: puede empeorar series con nivel inestable o muertas; vigilar familias pequeñas. Sin fuga si m14 usa solo días < corte |

**Orden recomendado** (de simple a compleja, una idea cada una): 4 (solo añade cortes, reutiliza código) → 2 → 3 → 1 → 5.
**Prioridad por valor**: 1 y 4 tocan el test de agosto, que es donde más se ha ganado en Kaggle (v0.7, v0.8); 2 y 3 son baratas;
5 es la más arriesgada y la que más enseña (cambiar *qué* se predice, no con qué rasgos).

Criterio para todas (CLAUDE.md): RMSLE medio < 0.3814 / 0.3815 con semillas 42 y 7, como mucho 1 de 4 folds peor; anotar control
sin cerradas (no empeorar) y, para 1 y 4, la predicción media en log de las tiendas 18 y 25 en el test frente a base-v9.

## 2/3 · Experto: dónde falla base-v9 y qué atacar primero (2026-10-18, T-090)

Detalle y casos en `docs/ANALISIS-ERRORES.md` (sección T-090). Predicciones de V-031 (= base-v9), semillas 42 y 7, solo folds.

**Lo que dicen los datos, en cuatro frases.** (a) El 84 % del error es el baile diario de series pequeñas: aunque acertásemos el nivel
exacto de cada serie en los 16 días, solo bajaríamos de 0.3814 a 0.3497. (b) Ese nivel no se puede adivinar con lo que hay en el corte:
el sesgo de cada serie no se repite entre folds (correlación ≤ 0.12) ni sigue a la tendencia o al año anterior, y restar el sesgo
reciente del modelo no mejora (0.3794 → 0.3794/0.3798 por familia; empeora por serie). (c) Lo único sistemático: **GROCERY II predice
de menos en 4/4 folds** (−0.06…−0.22; 6.6 % del error) porque su venta de 2017 está por encima de todo lo visto y el año anterior
(julio 2016, con bache) la arrastra hacia abajo; y **temporadas desplazadas** (material escolar tienda 45: la vuelta al cole de 2017
arranca 3 semanas antes que la de 2016; serie con más error). (d) Ceros, horizonte, paga y festivos ya no son un problema: el techo de
los ceros con información perfecta es −0.002.

**Descartado por los datos** (no proponer): corregir el sesgo con el error reciente del modelo (contrafactual sin fuga: no gana),
más reglas de ceros/intermitencia (techo −0.002, ya rechazadas V-015/V-022), festivos y paga (sin error que atacar en los folds).

| # | Idea | Hipótesis | Cambio concreto (uno solo) | Ganancia esperada | Coste (min) | Riesgo |
|---|---|---|---|---|---|---|
| E1 | **El año anterior solo como «forma», no como nivel** | `ly_day`/`ly_win` dan el nivel absoluto de hace un año; cuando una serie ha crecido (GROCERY II) o tuvo un bache en 2016 (tienda 19: 11 días a 0), anclan la predicción abajo. `ly_diff` ya dice «cuánto subió o bajó el año pasado en estas fechas», que es lo que generaliza | Quitar `ly_day` y `ly_win` de los rasgos del directo y del recursivo (`model.py` l. 82-83 y 116-123); dejar `ly_diff` | −0.0005…−0.0015 (GROCERY II, series con huecos en 2016) | 10 + 35 | Medio: v0.7/v0.8 ganaron en Kaggle con el año anterior; si la mejora viene de la forma, se conserva. Vigilar control c1 sin cerradas (0.3845) y SCHOOL en c1 (0.52): si empeoran > 0.002, rechazar aunque mejoren los folds |
| E2 | **Año anterior con ventana ancha** | Las temporadas no caen el mismo día cada año (vuelta al cole 2017 −3 semanas frente a 2016). Con ±3 días el modelo no ve que «algo grande viene»; con ±14 días sí | Añadir un rasgo `ly_win14` = media de log1p en t−364 ± 14 d (y su versión relativa `ly_diff14` = `ly_win14` − media 14 d previos a t−378), en directo y recursivo | −0.0003 en prácticas (f1, material escolar); probablemente más en Kaggle (agosto) | 15 + 35 | Medio (lección v0.6: lo de agosto puede ir al revés en Kaggle). Sin fuga: todo ≥ 350 d antes del objetivo. Mirar c1 y la predicción de SCHOOL del test frente a base-v9 |
| E3 | **Historia sin picos sueltos** | Un día raro (CLEANING tienda 32: 2962 en una serie de ~400) entra en medias y máximos y deforma los rasgos de las semanas siguientes | Antes de calcular rasgos (no objetivos): recortar log1p de cada día a mediana 56 d de la serie + 1.5 (≈ ×4.5) | −0.0002…−0.0008 | 15 + 35 | Bajo de fuga. Puede recortar arranques reales de temporada (material escolar): aplicar el tope con la mediana de los 56 d anteriores a *ese* día, no al corte |

**Apoyo con datos a ideas del modelador:** la 5 (predecir la diferencia con el nivel reciente) y la 2 (medias exponenciales) atacan el
mismo síntoma que E1 —GROCERY II por encima de lo visto—. E1 y la 5 son alternativas: si E1 gana, la 5 vale menos, y al revés.
La 1 (tiendas cerradas como dato que falta) no la veo en los folds de prácticas (las tiendas con más sesgo, 53 y 25, oscilan de signo
entre folds), pero sí importa en el test de Kaggle por las tiendas 18/25; mantenerla.

**Mi orden por valor** (el error más grande y sistemático primero): **E1** (barata, ataca la 2.ª familia en error) → 5 del modelador si
E1 no gana → **E2** (temporada; más valor en Kaggle que en prácticas) → 1 y 4 del modelador → **E3** (pequeña).
Expectativa honesta: cada idea 0.0005-0.0015; lo que queda es sobre todo ruido. Criterio: el de CLAUDE.md (< 0.3814 / 0.3815 con
semillas 42 y 7, como mucho 1 de 4 folds peor) más, para E1 y E2, no empeorar el control c1 sin cerradas en más de 0.002.

## 3/3 · Investigador: técnicas de la literatura que no hemos probado (2026-10-18, T-091)

Base: base-v9 (0.3814 / 0.3815). Leído: `model.py` (rasgos y `PARAMS`), `APRENDIZAJES.md` y las secciones 1/3 y 2/3. No repito EWM,
distancia a promo, dos vueltas al cole, objetivo relativo a m14, año anterior como forma, ventana ±14 ni recorte de picos (ya están
arriba), ni nada de la lista de rechazadas. **No hice búsqueda web nueva** en este turno: las fuentes son `docs/LECTURAS.md` (M5, M4,
Favorita) y la documentación de LightGBM (`linear_tree`, `huber`), citadas de memoria y sin reverificar.

**Huecos que nadie ha tocado:** (i) `stores.csv` (tipo, cluster, ciudad) no entra: el modelo solo conoce `store_nbr`; (ii) la pérdida
es L2 pura, sensible a picos sueltos en el *objetivo* (el 84 % del error es baile diario de series pequeñas); (iii) las hojas del
árbol son constantes y no extrapolan (GROCERY II por encima de lo visto, hallazgo c del experto); (iv) el modelo no sabe «cuánto lleva
viva» una serie (familias que empezaron en 2016, tiendas nuevas).

| # | Idea | Hipótesis | Cambio concreto (uno solo) | Ganancia esperada | Coste (min) | Riesgo |
|---|---|---|---|---|---|---|
| N1 | **Hojas lineales (`linear_tree`)** | Con una recta en cada hoja el modelo puede seguir una subida fuera de lo visto (GROCERY II, 2017 > 2016) sin cambiar rasgos. Ataca lo mismo que la 5 del modelador y E1, por otro camino | `linear_tree=True` (+ `linear_lambda=1.0`) en `PARAMS` del directo (no del recursivo) | −0.0005…−0.002 (incierta) | 10 + 60 (≈×2-3 más lento) | Medio: los `ly_*` son NaN a menudo y la regresión de la hoja los trata mal; si pasa de 15 min por medición, bajar rondas. Sin fuga |
| N2 | **Pérdida robusta (Huber) sobre log1p** | El objetivo tiene picos sueltos (p. ej. 2962 en una serie de ~400) y L2 los persigue. Huber los trata como L1 pasado un umbral. A diferencia de tweedie (V-007/V-032) sigue en escala log, alineada con RMSLE | `objective="huber"`, `alpha=1.0` (probar 0.7 si no cambia nada) en directo y recursivo | −0.0003…−0.001 | 8 + 35 | Bajo de fuga. Huber estima algo entre media y mediana → posible sesgo a la baja en series irregulares: mirar sesgo en log y c1 |
| N3 | **Metadatos de tienda** | 54 identificadores comparten poco; tipo (A-E), cluster (17) y ciudad agrupan tiendas parecidas y ayudan a las de poca historia | Añadir `store_type`, `store_cluster`, `store_city` (códigos categóricos, de `stores.csv`) al directo y al recursivo | −0.0003…−0.001 | 15 + 35 | Bajo de fuga (estáticos). Puede ser redundante con `store_nbr` (como V-028) o sobreajustar por ciudad. Mirar tiendas 18/25 en el test |
| N4 | **Edad de la serie** | Series recién nacidas (familias de 2016, tiendas nuevas) tienen la media de 56 d sesgada por el arranque; «días desde la primera venta» (tope 365) se lo dice | Rasgo `age` = días desde la primera venta > 0 hasta el corte, tope 365, en los dos submodelos | −0.0002…−0.0008 | 12 + 35 | Bajo. Se solapa con la 1 del modelador (cierres como dato que falta): medir encima de ella. Usar solo días < corte |

**Orden recomendado:** **N2** (un parámetro; enseña cómo la pérdida cambia qué error se persigue) → **N1** (pega con el hallazgo del
experto; más tope) → **N3** → **N4**.

| Idea | Ganancia | CPU | Dificultad | Qué se aprende |
|---|---|---|---|---|
| N2 Huber | baja | ×1 | muy baja | la pérdida decide qué error se persigue |
| N1 linear_tree | media (incierta) | ×2-3 | baja | por qué los árboles no extrapolan |
| N3 metadatos | baja | ×1 | baja | cuándo un dato estático ayuda o repite un identificador |
| N4 edad | baja | ×1 | baja | series que nacen: el arranque contamina las medias |

**Descartado tras pensarlo:** petróleo y transacciones (macro/agregado, sin señal a 16 días, misma lógica que V-028); redes
neuronales u otras librerías de árboles (no se pueden instalar, y V-010/V-032 muestran que sin diversidad real no hay ganancia);
Fourier del día del año (solo hay dos años: se memorizaría, como V-016).

**Expectativa honesta:** cada idea ≤ 0.002, cerca del ruido (~0.001); N1 es la de tope mayor. Criterio para todas: el de CLAUDE.md
(RMSLE medio < 0.3814 / 0.3815 con semillas 42 y 7, como mucho 1 de 4 folds peor; c1 sin cerradas no peor en más de 0.002;
> 15 min por medición solo si la ganancia es clara).
