# V-025: año anterior (V-018) sin copiar sus cierres
Como V-018, añade 4 cortes del mismo periodo del año anterior al modelo directo, pero descarta de esos ejemplos
las tiendas cerradas (≥50 % de días con venta total 0 en la ventana objetivo) y las series a 0 toda la ventana
que sí vendían en las 8 semanas previas. Así no aprende que en agosto "se hunden" las tiendas 18 y 25 (cerradas en 2016).
Solo cambia el bloque marcado V-025 en `fit_predict`.
