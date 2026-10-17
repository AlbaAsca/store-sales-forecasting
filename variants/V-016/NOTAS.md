# V-016: día del mes y día de paga
Añade al modelo directo y al recursivo 4 rasgos de calendario del día objetivo: día del mes, es_día_de_paga (15 y último día),
días desde la última paga y días a fin de mes. Motivo: base-v4 tiene sesgo por día del mes (días 1-5 y fin de mes infrapredichos).
Nada más cambia. Criterio: CV medio < 0.3858, ≤1 fold peor, mejora > 0.001 (otra semilla), c1 sin tiendas 18/25 ≤ 0.3902.
