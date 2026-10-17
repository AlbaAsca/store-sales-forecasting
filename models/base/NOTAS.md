# V-014 — afinado de hiperparámetros LightGBM
Solo cambia los hiperparámetros (hojas, lr, rondas, min_data), sin early stopping. Los valores de la base venían copiados de otra solución.
Los valores se leen de variables de entorno `HP_LEAVES`, `HP_LR`, `HP_ROUNDS`, `HP_MIN_DATA` para recorrer la rejilla sin editar código;
por defecto: 63 hojas, lr 0.03 × 700 rondas, min_data 100 (primera candidata; el quick corre: fold 1 = 0.3902).
Para el tester: medir la rejilla (18 combos, o por ejes desde base-v4: 31/0.05×400/50) con otra semilla (`--seed`); criterio: mejora < 0.002 = RECHAZADA (ruido).
