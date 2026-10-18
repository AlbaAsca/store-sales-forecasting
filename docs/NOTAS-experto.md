# Notas del experto

## 2026-10-18 · T-106 · El cambio de mes sí tiene error (V-038, RMSLE 0.3807; semillas 42 y 7 idénticas)

**Cómo leerlo:** en T-090 (`docs/ANALISIS-ERRORES.md`) el grupo «días de paga» salía bien (0.367) y se descartó. Pero ese
grupo mezclaba días en que el modelo se pasa con días en que se queda corto, y en la media se anulaban. Mirando el sesgo
**por fecha** (todas las series juntas) aparece un dibujo que se repite en cada fold: se pasa justo antes de la paga y se
queda corto justo después. Sesgo = media de `log(1+pred) − log(1+real)`; positivo = predice de más.
Fuente: `python scripts/analysis/errors_daybias.py V-038 V-038-s7` (solo folds f1-f4; holdout no mirado).

| Hallazgo | Evidencia |
|---|---|
| Días 1-4 del mes: predice **de menos** | Sesgo −0.088 (f2, 1-4 jul) y −0.071 (f4, 1-4 jun). Peor día: 4-jun −0.115, 2-jul −0.108 |
| Últimos días del mes (27-31): predice **de más** | +0.038 (f2), +0.052 (f3), +0.052 (f4); f1 −0.016 (27-30 jul). 29-30 may: +0.086 / +0.105 |
| Días 12-15 (antes de la paga del 15): de más en 4/4 folds | +0.025, +0.006, +0.022, +0.045. Días 16-19: ~0 |
| Es efecto de demanda, no ruido de series pequeñas | El sesgo diario de series grandes y pequeñas se parece (correlación 0.73); igual en las 2 semillas |
| Cuánto hay | Techo restando el sesgo medio de cada fecha (usa el futuro): 0.3807 → 0.3782. Solo con 5 tramos de día del mes: → 0.3794 (−0.0013), más que la mayoría de ideas recientes |

**Por qué V-016 no lo arregló:** le dio al árbol el día del mes en crudo y lo memorizó (pocas quincenas por fold). La idea
nueva es darle un *perfil*: cuánto vende cada tienda en esos tramos del mes respecto a su media, calculado con su propia
historia antes del corte, igual que el perfil semanal que sí funcionó (V-001). Ojo para Kaggle: el test (16-31 ago) solo
tiene los tramos 16-19 (sin sesgo) y 27-31 (de más), así que en Kaggle la ganancia esperable es menor que en CV.
Tarjeta: V-041 (perfil de paga).
