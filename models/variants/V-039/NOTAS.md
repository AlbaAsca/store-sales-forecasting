# V-039 — repesca de V-022 (series que se venden a ratos) sobre base-v10

Se añaden rasgos que dicen si una serie se vende a ratos: fracción de días con venta cero en 14/28/56 días (zfrac14/28/56) y días
desde la última venta (since_nz). V-022 mejoraba con 2 semillas y solo la frenó el holdout local, que ya falló 3 veces frente a Kaggle.
Novedad respecto a V-022: la base trata los días de tienda cerrada como dato que falta, así que estos rasgos los ignoran (no cuentan
un cierre como cero de venta). Cambio en _features y _step_feats (vía _zero_feats). Pendiente del tester: semillas 42 y 7.
