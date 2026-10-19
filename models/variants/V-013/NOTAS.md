# V-013: mezcla en log de base-v3 (LightGBM directo) y base-v2 (estadístico)

pred = expm1(w·log1p(v3) + (1-w)·log1p(v2)). Hipótesis: v2 falla distinto y reduce la varianza de v3.
Los modelos no se tocan; v3 = modo `direct` del código (equivale a V-006, porque `models/base` contiene hoy código de V-009).
`w` por defecto 0.8; el tester lo barre con la variable de entorno `V013_W` (0.6, 0.7, 0.8, 0.9) y elige en los folds.
Quick (fold 1, w=0.8): 0.3929. Criterio: media < 0.3904 y no empeora >1 fold; si w óptimo = 1.0, RECHAZADA.
