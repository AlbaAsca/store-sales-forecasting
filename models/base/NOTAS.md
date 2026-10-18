# V-037 — días de tienda cerrada = dato que falta

Antes, un día en que una tienda entera vendía 0 (cierre, 25-dic, días antes de abrir) entraba como un cero más en los promedios
y arrastraba el cierre de 2016 a las predicciones. Ahora esos días son NaN en los rasgos (medias, perfil semanal, ly_*) y las
medias usan nanmean. Los objetivos de entrenamiento y la regla del cero (V-023) siguen viendo la serie original.
Pendiente del tester: medir con semillas 42 y 7, control sin cerradas y predicción media de tiendas 18 y 25.
