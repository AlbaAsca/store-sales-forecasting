# V-036 — año anterior con ventana más ancha
Además de la ventana de ±3 días del año pasado, el modelo ve el promedio de ±14 días (`ly_win14`) y cuánto sube respecto a las 2 semanas previas (`ly_diff14`), en directo y recursivo.
Por qué: la vuelta al cole cae ~3 semanas antes en 2017 que en 2016; una ventana ancha capta que se acerca la temporada.
Todo usa datos ≥350 días anteriores al objetivo (sin fuga). No se trata el cierre de tiendas de forma especial (la base tampoco).
