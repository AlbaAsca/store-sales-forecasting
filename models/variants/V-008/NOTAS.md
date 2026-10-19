# V-008: 16 modelos directos (uno por horizonte)

Hipótesis: en vez de un LightGBM con `h` (1..16) como rasgo, se entrena uno por cada día de horizonte (estrategia multi-paso *directa*: cada modelo aprende solo a predecir "h días adelante" y se especializa).
Cambio: único, en `fit_predict`: se parte el conjunto apilado por `h`, se entrenan 16 modelos (mismos rasgos y parámetros, sin la columna `h`, 400 rondas) y cada uno predice su día.
Cada modelo ve 1/16 de las filas, así que puede ir más justo de datos; tarda ~16 entrenamientos pequeños en vez de uno grande.
Pendiente del tester: medición completa de 4 folds y repetición con otra semilla (criterio de la tarjeta). Humo `--quick` (f1): 0.4793.
