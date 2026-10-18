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
