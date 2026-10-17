# V-006 — estacionalidad anual (retardo 364) en el LightGBM global

Sobre V-005 (aceptada). Añade 3 rasgos: log1p de ventas del mismo día objetivo hace 364 d (mismo día de la semana), media de su ventana ±3 d,
y la diferencia entre esa ventana y la media log de los 14 d previos a ese día (cuánto subió el año pasado respecto a su nivel normal).
Por qué: ninguna media reciente ve picos anuales (p. ej. vuelta al cole, tienda 45). Nada más cambia.
Sin fuga: el retardo 364 d siempre queda antes del corte (horizonte 16). Sin historia previa → NaN (LightGBM lo gestiona).
Mirar SCHOOL AND OFFICE SUPPLIES. Medición y veredicto: tester.
