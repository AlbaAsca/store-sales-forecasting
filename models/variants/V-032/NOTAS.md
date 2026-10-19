# V-032: mezclar el modelo actual con uno entrenado con pérdida tweedie

Sobre la base-v8 se entrena un modelo extra (directo, historial medio) con pérdida tweedie sobre ventas sin comprimir.
Se mezcla en escala log: (1-w)·base + w·tweedie, con w = 0,2 por defecto (`--env V032_W=0.1|0.2|0.3`).
Sola, la tweedie era peor (V-007: 0,4094), pero se equivoca de otra forma y una pizca puede corregir errores de la base.
Medición completa pendiente del tester.
