# V-033 — banda de incertidumbre (intervalos)
Además de la previsión de siempre (que no cambia: mismo envío que la base), se entrenan tres modelos extra que predicen
el percentil 10, 50 y 90 de la venta (LightGBM `objective=quantile` en log1p, mismos rasgos, modelo directo de ventana media).
Así cada día tiene una banda «entre X e Y con 80 % de confianza».
`scripts/backtest.py` lee `INTERVALS` del modelo y guarda por fold, en `intervals`: cobertura 10-90, pinball de cada cuantil y RMSLE de la mediana.
Criterio: cobertura 0,75-0,85 en los 4 folds y mediana sin empeorar > 0,001 la RMSLE de la base. No se promueve.
Prueba rápida (fold f1): cobertura 0,786; RMSLE de la mediana sola 0,3967 (la previsión principal da 0,3877).
