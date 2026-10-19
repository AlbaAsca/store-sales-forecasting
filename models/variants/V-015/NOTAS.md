# V-015 — variables de intermitencia

Sobre base-v4. Se añaden 4 rasgos por serie (tienda×familia): fracción de días con venta 0 en los últimos 14/28/56 días
(`zfrac14/28/56`) y días desde la última venta (`since_nz`, tope 56), tanto en el modelo directo (`_features`) como en el recursivo (`_step_feats`).
Por qué: los ceros son el 8 % de las filas y el 22 % del error; el modelo no sabía si una serie es intermitente.
«Cero» = log1p(venta) < 0.1 (las predicciones recursivas no son 0 exactos). Quick fold 1: 0.3903 (veredicto: tester, 4 folds + semilla + control c1).
