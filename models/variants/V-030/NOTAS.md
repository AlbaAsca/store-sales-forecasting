# V-030: modelos con historiales de distinta longitud
Entrena 3 copias de la base: una mira solo el pasado reciente (ventanas 3/7/14 d), otra la base (hasta 56 d) y otra el pasado largo (28/112/364 d). Se promedian en log.
Idea: los modelos del ensemble ganador de Kaggle ven el pasado de formas muy distintas, y así sus errores se compensan más que con semillas.
Coste: ~3x tiempo (V-010 dio -0.0002 con x3; solo se acepta si gana claramente). `V030_CFGS=01` etc. selecciona subconjuntos.
Quick (fold 1, semilla 42): 0.3891, 72 s. Medición completa pendiente del tester.
