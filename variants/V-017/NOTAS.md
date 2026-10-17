# V-017: festivos por tienda
Se añaden 4 columnas 0/1 para el día a predecir: festivo nacional, regional (según el estado de la tienda), local (según su ciudad) y evento nacional. Se cruzan `holidays_events.csv` y `stores.csv` (vienen en `ctx`; es calendario, no ventas, sin fuga).
Reglas: festivo trasladado (`transferred=True`) = día normal; Transfer/Bridge/Additional = festivo; Work Day = laborable.
Entran tanto en el modelo directo como en el recursivo. Sin medir aún: queda para el tester (2 semillas, folds, c1 sin tiendas 18/25 y holdout).
