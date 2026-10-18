# V-031: tres historiales de distinta longitud sobre la base-v8

Se entrenan tres copias del modelo de la base-v8 (con promociones de días vecinos): una mira ~2 semanas de historial,
otra ~2 meses y otra ~1 año. Se promedian sus predicciones en escala log. Es la idea de V-030 (que mejoró pero se rechazó por tiempo)
aplicada a la base nueva, para ver si las mejoras se suman.
Prueba rápida (fold 1, semilla 42): 0.3877, 91 s. Medición completa pendiente del tester.
