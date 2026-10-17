# V-021 (= V-010 sobre base-v5)
Promedia 6 copias del modelo (3 semillas x 2 ventanas de historia: todo / desde 2015), en escala log, para reducir el ruido del azar.
En base-v4 mejoraba las 4 practicas por muy poco (0.3856 vs 0.3858) pero costaba x3 de tiempo; se repite con la regla nueva (2 semillas, mejora repetida).
Solo cambia fit_predict (envoltorio) respecto a models/base. Pendiente de medicion por el tester (semillas 42 y 7).
