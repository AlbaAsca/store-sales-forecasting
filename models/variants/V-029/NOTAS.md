# V-029: un modelo por familia de producto
Sobre base-v7, en vez de un LightGBM para las 33 familias se entrena uno por familia (tanto el directo como el recursivo),
para que cada uno se especialice en su patrón. Como cada modelo ve ~33 veces menos datos, se usan árboles más pequeños
(num_leaves 15, min_data 20, 300 rondas; ajustables con F_LEAVES, F_MIN_DATA, F_ROUNDS).
Prueba rápida (fold 1): 0.3946, 21 s. Falta medición completa con 2 semillas (tester).
