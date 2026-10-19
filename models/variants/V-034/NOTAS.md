# V-034 — reconciliación jerárquica
Además de las 1782 series tienda×familia, el mismo modelo predice total, 54 tiendas y 33 familias (ventas agregadas, con sus promociones sumadas).
Luego se ajustan todas las predicciones a la vez (mínimos cuadrados ponderados, pesos = nivel medio de cada serie; numpy, sin paquetes) para que las sumas cuadren, y se vuelve a log.
No se usa MinT con covarianza de residuos (no hay residuos dentro de muestra baratos): se usa la versión con varianza ∝ nivel. Las series que el modelo daba a 0 siguen en 0.
`--env RECON=0` apaga el ajuste (comparación limpia). Prueba rápida fold 1: con ajuste 0.3903, sin ajuste 0.3881 (una sola pasada; veredicto del tester).
