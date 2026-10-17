# V-010: ensemble de semillas y ventanas
Sobre base-v4 (avg recursivo+directo). Se entrena 6 veces (3 semillas x 2 ventanas: todo el historico / desde 2015-01-01) y se promedian las predicciones en log.
Por que: LightGBM con bagging tiene varianza por semilla y la ventana reciente evita arrastrar regimenes antiguos; promediar reduce ruido sin sesgo.
Coste: ~6x tiempo. Criterio: RMSLE medio < base-v4 (0.3858), empeora como mucho 1 de 4 folds, ganancia > variacion entre semillas (~0.001).
