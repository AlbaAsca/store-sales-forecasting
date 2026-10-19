# V-035: el año anterior solo como forma, no como nivel

Se quitan los rasgos `ly_day` y `ly_win` (cuánto se vendió hace 364 días) del modelo directo y del recursivo. Se mantiene `ly_diff`
(cuánto subió o bajó el año pasado en esas fechas respecto a las 2 semanas previas).
Motivo: GROCERY II se predice por debajo de lo real porque el modelo se ancla al nivel, más bajo, del año anterior.
Criterio: RMSLE medio < base con semillas 42 y 7, c1 sin cerradas ≤ 0.3845+0.002 y SCHOOL en c1 no peor de 0.002. Medición pendiente del tester.
