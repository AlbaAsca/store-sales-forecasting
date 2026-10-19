# V-001 — perfil por día de la semana

**Qué cambia:** la predicción sigue siendo la media de 14 días, pero se multiplica por un factor por tienda×familia y día de la semana
(media de ese día / media global, últimas 8 semanas). Sin dato o media 0 → factor 1.

**Por qué:** la base predice lo mismo cada día y se pierde la estacionalidad semanal (el fin de semana se vende más).

**Estado:** corre en el backtest rápido (f1 RMSLE 0.4368); medición completa pendiente del tester.
