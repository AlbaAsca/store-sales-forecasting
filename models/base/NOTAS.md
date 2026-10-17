# V-009 — estrategia recursiva y media directo+recursivo

Sobre base-v3 (directo: un LightGBM predice los 16 días de golpe desde la fecha de corte). Aquí se añade un modelo de **1 paso**
con lags cortos (1-7 d, medias 3/7/14/28/56, perfil semanal, promo, ly 364) entrenado con los últimos 150 días objetivo,
que predice mañana, se **realimenta** con su propia predicción y repite 16 veces.
Modos (variable de entorno `V009_MODE`): `rec` (por defecto, solo recursivo), `avg` (media en log de recursivo y directo), `direct` (= base-v3).
Medir los dos: `backtest.py --src variants/V-009 --name V-009-rec` y con `V009_MODE=avg` para `V-009-avg`. Quick fold 1: rec 0.3965, avg 0.3909 (veredicto: tester, 4 folds + otra semilla).
