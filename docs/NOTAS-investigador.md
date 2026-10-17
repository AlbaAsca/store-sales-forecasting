# Notas del investigador

## 2026-10-17 · ronda de aportación
Hallazgo (a partir de docs propios, sin búsqueda nueva): el modelo base NO tiene (a) rasgos de intermitencia/ceros ni (b) rasgos de calendario
(día del mes, paga 15/fin de mes). ANALISIS-ERRORES (#2): los ceros son el 8 % de filas y el 22 % del error; las series intermitentes aportan el 27 %.
El fold de control c1 (vuelta al cole) da 0.77 frente a 0.39: hay estructura de calendario que el modelo no ve.
Fuentes: docs/ANALISIS-ERRORES.md, docs/DISENO-MODELOS.md (chongzhenjie: zero_fc_window; M5: tweedie/ceros); la descripción de la competición
menciona la paga quincenal del sector público (días 15 y último). No verificado con búsqueda web en esta ronda.

Comparación (ganancia / CPU / dificultad / aprendizaje):
- V-015 rasgos de ceros (fracción de ceros 14/28/56 d, días desde última venta>0): media-alta / ≈0 / baja / intermitencia.
- V-016 calendario (día del mes, is_payday, días a fin de mes): media (mirar c1) / ≈0 / baja / cuándo ayuda un rasgo de fecha.
- Hurdle (clasificador de ceros + regresor): en RMSLE la media en log ya estima E[log1p y]; ganancia dudosa → no propuesto.

Tarjetas pendientes de crear (el comando `board.py add` fue denegado en esta sesión):
- V-015 (alta, 25 min): añadir zfrac14/28/56 y since_nz a `_features` y `_step_feats`. Criterio: media 4 folds < base, ≤1 fold peor; vigilar RMSLE en filas real=0 y c1.
- V-016 (media, 20 min): añadir dom, is_payday, dias_a_fin_mes. Criterio: media < base, ≤1 fold peor; c1 debe bajar; si solo mejora c1, anotar sin aceptar.
