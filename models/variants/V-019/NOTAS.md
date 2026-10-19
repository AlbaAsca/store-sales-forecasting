# V-019: predecir cero en series que llevan semanas sin vender
Sobre base-v5, regla dura tras el modelo: si una serie (tienda×familia) lleva ZERO_N días seguidos con ventas 0 justo antes del corte, se predice 0.
ZERO_N sale de la variable de entorno (por defecto 56); el tester debe probar 28/56/90 con los folds y fijar una sola constante.
Solo usa días anteriores al corte (sin fugas). Prueba rápida (fold 1, N=56): 0.3899.
