# V-012 — más cortes de entrenamiento + peso a lo reciente
Cambio: N_CUTS 8 → 24 (más ejemplos por serie) y peso exponencial por antigüedad del corte (vida media 120 días, `HALF_LIFE`). Rasgos y parámetros del LightGBM intactos.
Por qué: más historia da más ejemplos, y el peso evita que lo antiguo domine. Configuración elegida a priori; el tester puede probar N_CUTS 16/40 y otros HALF_LIFE.
Humo (fold 1, rápido): 0.3922, 17 s. Sin evaluar; veredicto del tester.
